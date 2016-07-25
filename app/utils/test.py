from zabbix_client import ZabbixServerProxy

url = "http://192.168.1.220"
s = ZabbixServerProxy(url)

s.user.login(user="Admin",password="zabbix")

#s.hostgroup.create(name="reboot")

groups = s.hostgroup.get({"filter":{"name":["reboot"]}})


for i in groups:
    if i["name"] == "reboot":
        group_id = i["groupid"]
        break

host = [
    {"ip":"172.16.31.12", "host":"yz-ms-web-01"},
    {"ip":"172.16.31.13", "host":"yz-ms-web-02"},
    {"ip":"172.16.31.14", "host":"yz-ms-web-03"},
    {"ip":"172.16.31.15", "host":"yz-ms-web-04"},
    {"ip":"172.16.31.16", "host":"yz-ms-web-05"},
]

for i in host:
    data = {
        "host": i["host"],
        "interfaces": [
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": i["ip"],
                "dns": "",
                "port": "10050"
            }
        ],
        "groups": [
            {
                "groupid": group_id
            }
        ]
    }
    #s.host.create(data)

templates = s.template.get({"output": "extend",
                            "filter": {
                                "name": [
                                    "Template OS Linux"
                                ]
                                }
                            }
                           )

for i in templates:
    if i["name"] == "Template OS Linux":
        template_id = i["templateid"]
        break

hosts = host.get("")

