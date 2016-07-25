from ..rpc import AutoLoad
from flask import current_app
from ..models import db, Zbhost, Server, GraphiteGroupKey, GraphiteKeys
import requests
import json


def api_action(mm='', params={}):
    autoload = AutoLoad(mm)
    for func in (autoload.is_valid_module, autoload.is_valid_method):
        try:
            if not func():
                return False
        except Exception:
            raise

    method = autoload.call_method()
    try:
        result = method(**params)
    except Exception:
        raise
    return result


def check_params(cls, params):
    for key, value in params.iteritems():
        if not (hasattr(cls, key)):
            raise Exception("{0} is not an valid attribute in {1}".format(key, cls))


def check_output(output,cls):
    if not isinstance(output, list):
        raise Exception('output is not list')

    for i in output:
        if not hasattr(cls, i):
            raise Exception("{0} is not a valid attribute".format(i))


class Zabbix(object):
    def __init__(self):
        self.url = current_app.config.get("ZABBIX_API_URL")
        self.user = current_app.config.get("ZABBIX_API_USER")
        self.password = current_app.config.get("ZABBIX_API_PASSWORD")
        self.zb = None
        self._login()

    def _login(self):
        from zabbix_client import ZabbixServerProxy
        self.zb = ZabbixServerProxy(self.url)
        self.zb.user.login(user=self.user, password=self.password)

    def __del__(self):
        if self.zb is not None:
            self.zb.user.logout()


def sync_zabbix_to_zbhost():
    z = Zabbix()
    hosts = z.zb.host.get(output=["hostid", "host"])
    info = z.zb.hostinterface.get(hostids=[x["hostid"] for x in hosts], output=["hostid", "ip"])
    hosts_in_db = db.session.query(Zbhost).filter(Zbhost.hostid.in_([x["hostid"] for x in hosts])).all()
    for x in hosts:
        for y in info:
            if x["hostid"] == y["hostid"]:
                x["ip"] = y["ip"]
    print hosts_in_db
    if not hosts_in_db:
        for x in hosts:
            db.session.add(Zbhost(**x))
        db.session.commit()


def sync_server_to_zbhost():
    zbhosts = db.session.query(Zbhost).all()
    servers = db.session.query(Server).filter(Server.inner_ip.in_([x.ip for x in zbhosts])).all()
    server_info = dict()
    for host in servers:
        server_info[host.inner_ip] = host.id

    print server_info
    for host in zbhosts:
        if not host.cmdb_hostid:
            db.session.query(Zbhost).filter(Zbhost.id==host.id).update({"cmdb_hostid": server_info[host.ip]})
            db.session.commit()


class Treeview(object):
    def __init__(self):
        self.product_info = api_action("product.get", {"output":["id", "module_letter", "pid"]})
        self.idc_info = api_action("idc.get", {"output":["id", "name"]})
        self.data = []

    def get_child_node(self):
        ret = []
        for p in filter(lambda x: True if x.get("pid", None) == 0 else False, self.product_info):
            node = {}
            node['text'] = p.get("module_letter", None)
            node['id'] = p.get("id", None)
            node["type"] = "service"
            node["nodes"] = self.get_grant_node(p.get("id", None))
            ret.append(node)
        return ret

    def get_grant_node(self, pid):
        ret = []
        for p in filter(lambda x: True if x.get("pid", None) == pid else False, self.product_info):
            node = dict()
            node['text'] = p.get("module_letter", None)
            node['id'] = p.get("id", None)
            node["type"] = "product"
            node["pid"] = pid
            ret.append(node)
        return ret

    def get(self, idc=False):
        child = self.get_child_node()
        if not idc:
            return child

    def replace_template(self, hostid, templateids):
        templates = list()
        for id in templateids:
            templates.append({"templateid": id})
        try:
            ret = self.zb.host.update(hostid=hostid, templates=templates)
        except Exception as e:
            return e.args


def get_zabbix_data(hosts):
    zabbix_data = db.session.query(Zbhost).filter(Zbhost.cmdb_hostid.in_([h["id"] for h in hosts])).all()
    zb = Zabbix()
    ret = list()
    for zbhost in zabbix_data:
        tmp = dict()
        tmp["hostname"] = zbhost.host
        tmp["templates"] = zb.zb.template.get(hostids=zbhost.hostid, output=["templateid", "name"])
        tmp["hostid"] = zbhost.hostid
        ret.append(tmp)
    return ret


def zabbix_link_template(hostid, templateid):
    ret = list()
    zb = Zabbix()
    for hid in hostid:
        linked = [t["templateid"] for t in zb.zb.template.get(hostids=hid)]
        linked.extend(templateid)
        ret.append(zb.replace_template(id, linked))
    return ret


def get_graphite_keys():
    url = "http://192.168.1.222/metrics/index.json"
    r = requests.get(url)
    data = json.loads(r.content)
    tmp = [m[m.index(".")+1:] for m in data if not m.startswith("carbon")]
    return list(set(tmp))


def get_hostlist_by_group(service_id, server_purpose):
    where = {
        "service_id": service_id,
        "server_purpose": server_purpose
    }
    hostlist = api_action("server.get", {"output": ["hostname"], "where": where})
    return [host["hostname"] for host in hostlist]


def get_product():
    products = api_action("product.get", {"output":["module_letter", "id", "pid"]})
    bus = [product for product in products if product['pid'] == 0]
    data = []
    for b in bus:
        sec_procuct = get_sec_product(product, b["id"])
        for p in sec_procuct:
            performance_data = {}
            service_id = b["id"]
            server_purpose = p["id"]
            performance_data["product"] = "{0}/{1}".format(b["module_letter"], p["module_letter"])
            performance_data["hostlist"] = get_hostlist_by_group(service_id, server_purpose)
            performance_data["item"] = get_graphite_key_by_group(server_purpose)
            data.append(performance_data)
    return data


def get_sec_product(products, pid):
    ret = []
    for pro in products:
        if pro["pid"] == pid:
            ret.append(pro)
    return ret


def get_graphite_key_by_group(server_purpose):
    graphite_key_ids = db.session.query(GraphiteGroupKey).filter_by(service_id=server_purpose).all()
    key_data = db.session.query(GraphiteKeys).filter(GraphiteKeys.id.in_(
        [graphite.key_id for graphite in graphite_key_ids])).all
    return [{"key": key.name, "type": key.type, "title": key.title} for key in key_data]
