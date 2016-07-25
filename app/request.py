# -*- coding:utf8 -*-

import requests
import json

url = "http://127.0.0.1:5000/api"
headers = {"content-type": "application/json"}


def send_request(json_data):
    response = requests.post(url, data=json.dumps(json_data), headers=headers)
    return response

json_get = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "idc.get",
    "params": {
        "order": "id desc",
        "where": {
            "phone": "123456"
            }
    },
    "auth": "string2"}

json_create = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "idc.create",
    "params": {
        "name": "BJ",
        "idc_name": "北京",
        "address": "亦庄",
        "email": "haha@123.com",
        "phone": "123456",
        "user_interface": "kobe",
        "user_phone": "1234567",
        "rel_cabinet_num": 50,
        "pact_cabinet_num": 60,
    },
    "auth": "string2"}

json_update = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "idc.update",
    "params": {
        "data": {"phone": "22222"},
        "where": {
            "id": 2
            }
    },
    "auth": "string2"}

json_delete = {
    "jsonrpc": "2.0",
    "id": 3,
    "method": "idc.delete",
    "params": {
        "where": {"id": 11}
    },
    "auth": "string2"}


a = send_request(json_create)
print a.content
