import sys
import time
import uuid

import tornado.web
import json
from redis_helper import redis_helper
import payjz


class PaymentHandler(tornado.web.RequestHandler):
    def prepare(self):
        if "Content-Type" in self.request.headers:
            content_type = self.request.headers['Content-Type']
            if content_type == 'application/x-json' or content_type == 'application/json':
                self.args = json.loads(self.request.body)

    def get(self):
        with open("../config/price_info.json") as f:
            price_info = json.load(f)
            self.write(price_info)

    def post(self):
        if "time" not in self.args or "shop_num" not in self.args or "mac" not in self.args or "price" not in self.args:
            self.write({"code": 400, "msg": "request data error"})
            return
        order = {
            'body': 'test',  # 订单标题
            'out_trade_no': uuid.uuid4(),  # 订单号
            'total_fee': int(self.args["price"]),  # 金额,单位:分
        }
        ret = payjz.get_qr_code(order)
        if ret:
            self.args["out_trade_no"] = ret["out_trade_no"]
            self.args["payjs_order_id"] = ret["payjs_order_id"]
            self.args["qrcode"] = ret["qrcode"]
            self.args["code_url"] = ret["code_url"]
            self.args["date"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            redis_helper.hash_hset("payment", self.args["mac"], "")
            ret["code"] = 200
            ret["msg"] = "success"
            self.write(ret)
        else:
            self.write({"code": 400, "msg": "request qr code failed"})
