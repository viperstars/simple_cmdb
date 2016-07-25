#!/usr/bin/env python
# coding:utf-8

import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "abcdefg"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "mysql://rpc:123456@127.0.0.1/rpc"
    ZABBIX_API_URL = "http://192.168.1.220/"
    ZABBIX_API_USER = "Admin"
    ZABBIX_API_PASSWORD = "zabbix"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s- %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(os.path.join(basedir, 'flask.log'))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
