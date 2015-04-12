import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

define("port", default=8000, help="Run on the given port", type=int)

clients = dict()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, **kwargs):
        if "Id" in kwargs.keys():
            print("Your client id is: %s" % (kwargs["Id"],))
        self.render("index.html")
        #self.finish()


class MyWebSocketHandler(tornado.websocket.WebSocketHandler):
    id = None

    def open(self, *args, **kwargs):
        self.id = kwargs["Id"]
        self.stream.set_nodelay(True)
        clients[self.id] = self

    def on_message(self, message):
        print("Client %s received a message: %s" % (self.id, message))
        # send message to all clients
        for client in clients:
            h = clients[client]
            h.write_message('{"client_id": "%s", "message": "%s"}' % (self.id, message))


    def on_close(self):
        if self.id in clients:
            del clients[self.id]

    def check_origin(self, origin):
        return True


app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/(?P<Id>\w*)', MyWebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


