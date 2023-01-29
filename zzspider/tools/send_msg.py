import json

import requests


def sendMsg(msg, title, group):
    requests.post(
        url="http://api.day.app/push",
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "body": msg,
            "device_key": "S7weFcCSQ449MiKrn8uavn",
            "title": title,
            "ext_params": {
                "badge": 1,
                "group": group
            },
            "category": "category"
        })
    )