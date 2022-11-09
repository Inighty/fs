# -*- coding: utf-8 -*-
import configparser
import json
import os

from watchdog.events import *

logger = logging.getLogger(__name__)


def json_serialize(obj):
    obj_dic = class2dic(obj)
    return json.dumps(obj_dic, ensure_ascii=False, indent=2)


def value2py_data(value):
    if '.' in str(type(value)):
        # value 为自定义类
        value = class2dic(value)
    elif str(type(value)) == "<class 'list'>":
        # value 为列表
        for index in range(0, value.__len__()):
            value[index] = value2py_data(value[index])
    return value


def class2dic(obj):
    obj_dic = obj.__dict__
    for key in obj_dic.keys():
        value = obj_dic[key]
        obj_dic[key] = value2py_data(value)
    return obj_dic


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        update_rules()

    def on_created(self, event):
        update_rules()

    def on_deleted(self, event):
        update_rules()

    def on_modified(self, event):
        update_rules()


def update_rules():
    ConfigUtil.config = configparser.ConfigParser()
    # config.read('config.ini')
    config_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config_env,ini')
    ConfigUtil.config.read([config_env_path], encoding='utf-8')


class ConfigUtil(object):
    config = configparser.ConfigParser()
    # config.read('config.ini')
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config,ini')
    config_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config_env,ini')
    config.read([config_path, config_env_path], encoding='utf-8')

    # observer = Observer()
    # event_handler = FileEventHandler()
    # observer.schedule(event_handler, config_env_path, True)
    # observer.start()
