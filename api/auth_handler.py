import tornado.web


class AuthHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("AuthHandler: Hello, world")
