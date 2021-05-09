#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
from redis_helper import redis_helper
import json


class UpdateHandler(tornado.web.RequestHandler):
    def prepare(self):
        if "Content-Type" in self.request.headers:
            content_type = self.request.headers['Content-Type']
            if content_type == 'application/x-json' or content_type == 'application/json':
                self.args = json.loads(self.request.body)

    def get(self):
        self.write("UpdateHandler is OK")

    def post(self):
        if "time" not in self.args or "shop_num" not in self.args or "mac" not in self.args:
            self.send_error(400)
        redis_helper.list_lpush("")
