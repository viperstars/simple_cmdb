#!/usr/bin/env python
# -*- coding:utf8 -*-

from __future__ import unicode_literals
from . import main
from flask import current_app,jsonify,request
import os
from .. import rpc


@main.route('/', methods=['GET','POST'])
def index():
    current_app.logger.debug('ok')
    return 'index'

@main.route("/api", methods=['GET', 'POST'])
def api():
    current_app.logger.debug("ok")
    cur_dir=os.path.curdir
    json_data = request.json
    r = rpc.JsonRPC(json_data)
    r.execute()
    return jsonify(r.response.to_dict())
