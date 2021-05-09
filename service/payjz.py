import requests
import hashlib
from urllib.parse import urlencode,unquote
'''
扫码支付（主扫）
'''
key = '1603416270'                  # 填写通信密钥
mchid = 'tPC9ZEBdwVTRc8Fw'          # 特写商户号
notify_url = ''  # 'http://47.106.130.114/pay_server/payjz'


def get_qr_code(order):
    order['notify_url'] = notify_url
    order['mchid'] = mchid
    order['sign'] = sign(order)
    request_url = "https://payjz.cn/api/native"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=order, headers=headers)
    if response:
        return response.json()
    else:
        return None


# 构造签名函数
def sign(attributes):
    attributes_new = {k: attributes[k] for k in sorted(attributes.keys())}
    return hashlib.md5((unquote(urlencode(attributes_new))+'&key='+key).encode(encoding='utf-8')).hexdigest().upper()

