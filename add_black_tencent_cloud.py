import json

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models

secret_id, secret_key = "", ""
instance_id = ""
region = ""
ip = [
    "1.2.3.4",
    "2.3.4.5",
]


def get_version(client):
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.DescribeFirewallRulesRequest()
    params = {
        "InstanceId": instance_id,
        "Offset": 0,
        "Limit": 100
    }
    req.from_json_string(json.dumps(params))
    # 返回的resp是一个DescribeFirewallRulesResponse的实例，与请求对象对应
    resp = client.DescribeFirewallRules(req)
    # 输出json格式的字符串回包
    return resp.FirewallVersion


def add_firewall(client, version, rules):
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.CreateFirewallRulesRequest()
    params = {
        "InstanceId": instance_id,
        "FirewallRules": rules,
        "FirewallVersion": version
    }
    req.from_json_string(json.dumps(params))
    # 返回的resp是一个CreateFirewallRulesResponse的实例，与请求对象对应
    resp = client.CreateFirewallRules(req)
    # 输出json格式的字符串回包
    print(resp.to_json_string())


def build_data(ip):
    return [{"Protocol": "TCP", "Port": "ALL", "CidrBlock": item, "Action": "DROP", "FirewallRuleDescription": ""} for
            item in ip]


rules = build_data(ip)

try:
    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey,此处还需注意密钥对的保密
    # 密钥可前往https://console.cloud.tencent.com/cam/capi网站进行获取
    cred = credential.Credential(secret_id, secret_key)
    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    httpProfile = HttpProfile()
    httpProfile.endpoint = "lighthouse.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化要请求产品的client对象,clientProfile是可选的
    client = lighthouse_client.LighthouseClient(cred, region, clientProfile)

    version = get_version(client)
    add_firewall(client, version, rules)

except TencentCloudSDKException as err:
    print(err)
