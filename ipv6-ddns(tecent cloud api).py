import socket
import requests
import time,random
import hmac
import base64
import json
from hashlib import sha256
from urllib import parse
import sys
addrs = socket.getaddrinfo(socket.gethostname(),None)
ipv6_addr = addrs[1][4][0] #获取不到ipv6地址，或者想改ipv4什么的，请调整这个下标
domain = "yourdomain.com" #你的域名
subDomain = "sub" #要设置ddns的子域名
#我不保证可以用中文域名
class api(object):
    def __init__(self):
        self.Id = "" #请在https://console.cloud.tencent.com/cam/capi 生成密钥对并填入此处
        self.Key = "" #请在https://console.cloud.tencent.com/cam/capi 生成密钥对并填入此处
        self.url = "cns.api.qcloud.com/v2/index.php?"
        self.Public = {
            "Timestamp":str(int(time.time())),
            "Nonce":str(random.randint(1,10000)),
            "SecretId":self.Id,
            "SignatureMethod":"HmacSHA256",
        }
    def HmacSHA256(self,appsecret,data):
        return(base64.b64encode(hmac.new(appsecret, data, digestmod=sha256).digest()).decode("utf8"))
    def get(self,Private):
        Final = {**self.Public, **Private}
        keysorted = sorted(Final.keys())
        data = "GET"+self.url
        for i in keysorted:
            data = data+i+"="+Final[i]+"&"
        data = data[:-1]
        Signature = parse.quote(self.HmacSHA256(self.Key.encode('utf8'),data.encode('utf8'))).replace('/', '%2F')
        print(Signature)
        url = "https://"+data[3:]+"&Signature="+Signature
        return requests.get(url).json()

PrivateRecordList = {
    "Action":"RecordList",
    "domain":domain,
}
getRecordList = api()
RecordList = getRecordList.get(PrivateRecordList)
records = RecordList["data"]["records"]
recordid = ""
for record in records:
    if record["name"] == "homev6":
        if record["value"] == ipv6_addr:
            print("不用改")
            sys.exit(0)
        recordid = record["id"]
        break
PrivateRecordModify = {
    "Action":"RecordModify",
    "domain":domain,
    "recordId":str(recordid),
    "subDomain":subDomain,
    "recordType":"AAAA",
    "recordLine":"默认",
    "value":ipv6_addr,
}
while True:
    RecordModify = api()
    r = RecordModify.get(PrivateRecordModify)
    print(r)
    if r["code"] == 0:
        print("修改完毕")
        break
    print("失败")
