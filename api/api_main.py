#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from payment_handler import PaymentHandler
from update_handler import UpdateHandler
from auth_handler import AuthHandler
from payjz_handler import PayjzHandler

if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/pay_server/payment", PaymentHandler),
        (r"/pay_server/update", UpdateHandler),
        (r"/pay_server/auth", AuthHandler),
        (r"/pay_server/payjz", PayjzHandler),
    ])
    application.listen(8080)
    tornado.ioloop.IOLoop.current().start()
