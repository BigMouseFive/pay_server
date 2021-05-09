import tornado.web
import json
from redis_helper import redis_helper
import payjz

'''
return_code	int(1)	Y	1：支付成功
total_fee	int(16)	Y	金额。单位：分
out_trade_no	string(32)	Y	用户端自主生成的订单号
payjs_order_id	string(32)	Y	订单号
transaction_id	string(32)	Y	微信用户手机显示订单号
time_end	string(32)	Y	支付成功时间
openid	string(32)	Y	用户OPENID标示，本参数没有实际意义，旨在方便用户端区分不同用户
attach	string(127)	N	用户自定义数据
mchid	string(16)	Y	商户号
sign	string(32)	Y	数据签名 详见签名算法
'''


class PayjzHandler(tornado.web.RequestHandler):
    def prepare(self):
        if "Content-Type" in self.request.headers:
            content_type = self.request.headers['Content-Type']
            if content_type == 'application/x-json' or content_type == 'application/json':
                self.args = json.loads(self.request.body)

    # after client pay by qr code, check for pay operation response
    def get(self):
        out_trade_no = self.get_argument("out_trade_no", "")
        if out_trade_no == "":
            self.write({"code": 400, "msg": "there no out_trade_no in argument"})
            return
        value = redis_helper.hash_hget("payjs_order", out_trade_no)
        if value is None:
            self.write({"code": 400, "msg": "please wait"})
            return
        self.write({"code": 200, "msg": "success"})

    # payjz result notify
    def post(self):
        if self.args["return_code"] == 1:
            # 1. 验签逻辑
            sign_code = self.args.pop("sign")
            if sign_code != payjz.sign(self.args):
                self.write("sign failed")
                return
            # 2. 验重逻辑
            if redis_helper.hash_hget("payjs_order", self.args["out_trade_no"]):
                self.write("duplicate recieve")
            # 3. 自身业务逻辑
            redis_helper.hash_hset("payjs_order", self.args["out_trade_no"], self.args, "json")
            # 4. 返回success字符串（http状态码为200）
            self.write("success")
        else:
            self.write("return_code is not 1")
