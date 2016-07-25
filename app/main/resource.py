# -*- coding:utf8 -*-

from . import main
from flask import request, render_template
from ..utils import api_action
from ..models import db, Zbhost, Server
import json
from ..utils import Zabbix, sync_zabbix_to_zbhost, sync_server_to_zbhost, Treeview
from zabbix_client import JSONRPCError


@main.route("/resources/idc")
def resources_idc():
    ret = api_action("idc.get")
    return render_template("resources/server_idc_list.html",
                           title="idc",
                           idcs=ret)


@main.route("/resources/idc/modify/<int:id>")
def resources_idc_modify(id):
    ret = api_action('idc.get', {"where":{"id":id}})
    if ret:
        return render_template("resource/server_idc_modify.html",
                        titie="idc",
                        idc=ret[0])
    else:
        return render_template("404.html")


@main.route("/resources/idc/update", methods=["POST"])
def resources_idc_update():
    data = request.form.to_dict()
    id = data.pop("id")
    ret = api_action('idc.update', {"where": {"id": id}, "data":data})
    if ret:
        return render_template("public/success.html", next_url="/resources/idc/")
    else:
        return render_template("public/success.html", next_url="/resources/idc/")


@main.route("/resources/idc/add/")
def resources_idc_add():
    return render_template("resources/server_idc_add.html")


@main.route("/resources/idc/doadd/", methods=["POST"])
def resources_idc_doadd():
    data = request.form.to_dict()
    ret = api_action("idc.create", data)
    if ret:
        return render_template("public/success.html", next_url="/resources/idc/")
    else:
        return render_template("public/failure.html", next_url="/resources/idc/")


@main.route("/resources/server/manufacturers/add/", methods=["GET"])
def resources_manufacturers_add():
    ret = api_action("manufacturers.get")
    return render_template("resources/server_add_manufacturers.html")


@main.route("/resources/server/manufacturers/doadd/", methods=["POST"])
def resources_manufacturers_doadd():
    data = request.form.to_dict()
    ret = api_action("manufacturers.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/manufacturers/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/manufacturers/add")


@main.route("/resources/server/add/", methods=["GET"])
def resources_server_add():
    ret1 = api_action("manufacturers.get")
    ret2 = api_action("product.get", {"where":{"pid":0}})
    ret3 = api_action("idc.get")
    ret4 = api_action("raid.get")
    ret5 = api_action("raidtype.get")
    ret6 = api_action("status.get")
    ret7 = api_action("power.get")
    ret8 = api_action("supplier.get")
    ret9 = api_action("managementcard.get")
    return render_template("resources/server_add.html",
                           manufacturers=ret1,
                           products=ret2,
                           idc_info=ret3,
                           raids=ret4,
                           raidtypes=ret5,
                           status=ret6,
                           powers=ret7,
                           suppliers=ret8,
                           managementcardtypes=ret9)


@main.route("/resources/server/servertype/add/", methods=["GET"])
def resources_servertype_add():
    ret = api_action("manufacturers.get")
    return render_template("resources/server_add_servertype.html", manufacturers=ret)


@main.route("/resources/server/servertype/doadd/", methods=["POST"])
def resources_servertype_doadd():
    data = request.form.to_dict()
    ret = api_action("servertype.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/servertype/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/servertype/add")


@main.route("/resources/ajax/get_server_type/")
def resources_ajax_get_server_type():
    data = request.args.to_dict()
    ret = api_action("servertype.get", data)
    if ret:
        return json.dumps(ret)
    else:
        return json.dumps('')


@main.route("/resources/ajax/get_server_product/")
def resources_ajax_get_server_product():
    data = request.args.to_dict()
    ret = api_action("product.get", {"output": ["id", "service_name", "pid"], "where": data})
    if ret:
        return json.dumps(ret)
    else:
        return json.dumps('')


@main.route("/resources/ajax/get_cabinet/")
def resources_ajax_get_server_cabinet():
    data = request.args.to_dict()
    ret = api_action("cabinet.get", {"output": ["id", "name"], "where": data})
    if ret:
        return json.dumps(ret)
    else:
        return json.dumps('')


@main.route("/resources/server/product/add/", methods=["GET"])
def resources_product_add():
    ret = api_action("product.get")
    return render_template("resources/server_add_product.html", products=ret)


@main.route("/resources/server/product/doadd/", methods=["POST"])
def resources_product_doadd():
    data = request.form.to_dict()
    ret = api_action("product.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/product/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/product/add")


@main.route("/resources/server/cabinet/add/", methods=["GET"])
def resources_cabinet_add():
    ret = api_action("idc.get")
    ret1 = api_action("power.get")
    return render_template("resources/server_add_cabinet.html", idcs=ret, powers=ret1)


@main.route("/resources/server/cabinet/doadd/", methods=["POST"])
def resources_cabinet_doadd():
    data = request.form.to_dict()
    ret = api_action("cabinet.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/cabinet/product/add")
    else:
        return render_template("public/failure.html", next_url="/resources/cabinet/product/add")


@main.route("/resources/server/raid/add/", methods=["GET"])
def resources_raid_add():
    ret = api_action("raidtype.get")
    return render_template("resources/server_add_raid.html", raidtypes=ret)


@main.route("/resources/server/raid/doadd/", methods=["POST"])
def resources_raid_doadd():
    data = request.form.to_dict()
    ret = api_action("raid.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/raid/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/raid/add")


@main.route("/resources/server/raidtype/add/", methods=["GET"])
def resources_raidtype_add():
    ret = api_action("raidtype.get")
    return render_template("resources/server_add_raidcardtype.html", products=ret)


@main.route("/resources/server/raidtype/doadd/", methods=["POST"])
def resources_raidtype_doadd():
    data = request.form.to_dict()
    ret = api_action("raidtype.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/raidtype/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/raidtype/add")


@main.route("/resources/server/status/add/", methods=["GET"])
def resources_status_add():
    return render_template("resources/server_add_status.html")


@main.route("/resources/server/status/doadd/", methods=["POST"])
def resources_status_doadd():
    data = request.form.to_dict()
    ret = api_action("status.create", data)
    print ret
    if ret:
        return render_template("public/success.html", next_url="/resources/server/status/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/status/add")


@main.route("/resources/server/managementcard/add/", methods=["GET"])
def resources_management_add():
    return render_template("resources/server_add_managementcardtype.html")


@main.route("/resources/server/managementcard/doadd/", methods=["POST"])
def resources_managementcard_doadd():
    data = request.form.to_dict()
    ret = api_action("managementcard.create", data)
    if ret:
        return render_template("public/success.html", next_url="/resources/server/managementcard/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/managementcard/add")


@main.route("/resources/server/power/add/", methods=["GET"])
def resources_power_add():
    return render_template("resources/server_add_power.html")


@main.route("/resources/server/power/doadd/", methods=["POST"])
def resources_power_doadd():
    data = request.form.to_dict()
    ret = api_action("power.create", data)
    if ret:
        return render_template("public/success.html", next_url="/resources/server/power/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/power/add")


@main.route("/resources/server/supplier/add/", methods=["GET"])
def resources_supplier_add():
    return render_template("resources/server_add_supplier.html")


@main.route("/resources/server/supplier/doadd/", methods=["POST"])
def resources_supplier_doadd():
    data = request.form.to_dict()
    ret = api_action("supplier.create", data)
    if ret:
        return render_template("public/success.html", next_url="/resources/server/supplier/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/supplier/add")


@main.route("/resources/server/doadd/", methods=["POST"])
def resources_server_doadd():
    data = request.form.to_dict()
    print data
    ret = api_action("server.create", data)
    if ret:
        return render_template("public/success.html", next_url="/resources/server/add")
    else:
        return render_template("public/failure.html", next_url="/resources/server/add")


@main.route("/resources/server/modify/<int:id>", methods=["GET"])
def resources_server_edit(id):
    ret = api_action("server.get", {"where":{"id": id}})
    ret1 = api_action("manufacturers.get")
    ret2 = api_action("product.get", {"where": {"pid": 0}})
    ret3 = api_action("idc.get")
    ret4 = api_action("raid.get")
    ret5 = api_action("raidtype.get")
    ret6 = api_action("status.get")
    ret7 = api_action("power.get")
    ret8 = api_action("supplier.get")
    ret9 = api_action("managementcard.get")
    ret10 = api_action("cabinet.get")
    return render_template("resources/server_edit.html",
                           server=ret[0],
                           manufacturers=ret1,
                           products=ret2,
                           idcs=ret3,
                           raids=ret4,
                           raidtypes=ret5,
                           statuses=ret6,
                           powers=ret7,
                           suppliers=ret8,
                           managementcardtypes=ret9,
                           cabinets=ret10)


@main.route("/resources/server/update/", methods=["POST"])
def resources_server_update():
    data = request.form.to_dict()
    ret = api_action("server.update", {"where":{"id":data["id"]}, "data":data})
    if ret:
        return render_template("public/success.html", next_url="/resources/server/edit")
    else:
        return render_template("public/failure.html", next_url="/resources/server/edit")


@main.route("/resources/server/list", methods=["GET"])
def resources_server_list():
    ret = api_action("server.get")
    return render_template("resources/server_list.html", servers=ret)


@main.route("/resources/server/report/", methods=["POST"])
def resource_server_report():
    params = request.form.to_dict()

    where = {}
    if params.get("st", None) and len(params) > 3:
        where["st"] = params.pop("st")
    else:
        where["uuid"] = params.pop("uuid")

    host = api_action("server.get", {"where": where})

    if host:
        api_action("server.update", {"where": {"id": host[0]["id"]}, "data": params})
    else:
        params.update(where)
        api_action("server.create", params)
    return ""


@main.route("/resource/monitor/ajax/get_sync_zabbix_hosts", methods=["POST"])
def get_sync_zabbix_hosts():
    zabbix_hosts = db.session.query(Zbhost).all()
    hostip = [zb.ip for zb in zabbix_hosts]
    servers = db.session.query(Server).filter(~Server.inner_ip.in_(hostip)).all()
    return json.dumps([{"hostname": x.hostname, "id": x.id} for x in servers])


@main.route("/resource/monitor/ajax/sync_host_to_zabbix", methods=["POST"])
def resource_ajax_sync_host():
    params = request.form.to_dict()
    print params
    hostids = params["hostids"].split(",")
    servers = db.session.query(Server).filter(Server.id.in_(hostids)).all()
    server_num = len(servers)
    a = Zabbix()
    ret = []
    error = []
    for x in servers:
        d = {
            "host": x.hostname,
            "interfaces": [
                {
                    "type": 1,
                    "useip": 1,
                    "dns": "",
                    "main": 1,
                    "ip": x.inner_ip,
                    "port": "10051"
                }
            ],
            "groups": [
                {
                    "groupid": params["groupid"]
                }
            ]
        }
        try:
            ret.append(a.zb.host.create(**d))
        except JSONRPCError as e:
            error.append(e.data)
    sync_zabbix_to_zbhost()
    sync_server_to_zbhost()
    if len(ret) == server_num:
        return "1"
    else:
        return json.dumps("\n".join(error))


@main.route("/resources/monitor/zabbix/", methods=["GET"])
def resource_monitor_zabbix():
    zb = Zabbix()
    templates = zb.zb.template.get(output=["templateid", "name"])
    templates_data = list()
    for temp in templates:
        templates_data.append({"label": temp["name"], "value": temp["templateid"]})
    tv = Treeview()
    treeview = tv.get()
    return render_template("monitor/monitor_zabbix.html",
                           treeview=json.dumps(treeview),
                           templates=json.dumps(templates_data))
