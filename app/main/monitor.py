# -*- coding:utf8 -*-

from . import main
from ..utils import Zabbix, api_action, get_zabbix_data, zabbix_link_template, get_graphite_keys, Treeview
from flask import request, render_template
from app.models import GraphiteGroupKey, GraphiteKeys, db
import json


@main.route("/monitor/ajax/get_zabbix_host_groups", methods=["POST"])
def monitor_get_zabbix_host_groups():
    a = Zabbix()
    data = a.zb.hostgroup.get(output=["groupid","name"])
    return json.dumps(data)


@main.route("/monitor/ajax/get_zabbix_data_by_group/", methods=["POST"])
def monitor_ajax_get_zabbix_data_by_group():
    params = request.form.to_dict()
    hosts = api_action("server.get", {"output": ["id"],
                                      "where": {"server_purpose": params["server_purpose"],
                                                "service_id": params["service_id"]}})
    ret = get_zabbix_data(hosts)
    print ret
    return json.dumps(ret)


@main.route("/monitor/ajax/unlink_zabbix_template/", methods=["POST"])
def monitor_ajax_unlink_zabbix_template():
    params = request.form.to_dict()
    zb = Zabbix()
    ret = zb.zb.host.update(hostid=params["hostid"], templates_clear=params["templateid"])
    if ret:
        return "1"
    else:
        return ret


@main.route("/monitor/ajax/link_zabbix_template/", methods=["POST"])
def monitor_ajax_link_zabbix_template():
    params = request.form.to_dict()
    hostids = params["hostids"].split(",")
    templateids = params["template_ids"].split(",")
    ret_data = zabbix_link_template(hostids, templateids)
    flag = True
    for ret in ret_data:
        if not isinstance(ret, dict):
            flag = False
    if flag:
        return "1"
    else:
        return json.dumps(ret_data)


@main.route("/monitor/graphite/keys/")
def monitor_graphite_keys():
    keys = db.session.query(GraphiteKeys).all()
    return render_template("monitor/monitor_graphite_keys.html", graphite_keys=keys)


@main.route("/monitor/graphite/keys/add/", methods=["POST"])
def monitor_graphite_keys_add():
    data = request.form.to_dict()
    try:
        db.session.add(GraphiteKeys(**data))
        db.session.commit()
    except Exception as e:
        return e.args
    return '1'


@main.route("/monitor/ajax/graphite/get_keys/", methods=["POST"])
def monitor_ajax_graphite_get_keys():
    keys = get_graphite_keys()
    return json.dumps(keys)


@main.route("/monitor/ajax/graphite/group/get_keys/", methods=["POST"])
def monitor_ajax_graphite_group_get_keys():
    data = request.form.to_dict()
    g = db.session.query(GraphiteGroupKey).filter_by(**data).all()
    key_ids = [str(x.key_id) for x in g]
    return json.dumps(key_ids)


@main.route("/monitor/graphite/groups/")
def monitor_graphite_add_key_group():
    g = db.session.query(GraphiteKeys).all()
    key = []
    for s in g:
        key.append({"value": s.id, "text": s.name})

    tv = Treeview()
    treeview = tv.get()
    return render_template("monitor/graphite_group_keys.html",
                           treeview=json.dumps(treeview),
                           hosts=json.dumps(key))


@main.route("/monitor/ajax/graphite/add/key/group/", methods=["POST"])
def monitor_ajax_graphite_add_key_group():
    data = request.form.to_dict()
    r = db.session.query(GraphiteGroupKey).filter_by(**data).all()
    print r
    if not r:
        try:
            db.session.add(GraphiteGroupKey(**data))
            db.session.commit()
        except Exception as e:
            return e.args
        return "1"
    return "400"

@main.route()
