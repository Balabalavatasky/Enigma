import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import datetime
import persudoDatabase
from tornado import gen
from tornado.web import RequestHandler
from tornado.options import define, options
from tornado.websocket import WebSocketHandler

define("port", default=8000, type=int)

class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")

class AdminHandler(RequestHandler):
    def get(self):
        self.render("register.html")

class RegisterHandler(RequestHandler):
    def get(self,sensorId):
        print(sensorId)
        if sensorId!=None and not persudoDatabase.database.sensors.__contains__(sensorId):
            persudoDatabase.database.sensors[sensorId]=self
            msg='sensor %s is Registered'%(sensorId)
            print(msg)
            self.write(msg)
        else:
            self.write_error(400,'fail!')

class CancellationHandler(RequestHandler):
    def get(self,sensorId):
        if sensorId!=None and persudoDatabase.database.sensors.__contains__(sensorId):
            print('sensor Cancellation!')
            persudoDatabase.database.sensors.pop(sensorId)

class SensorHandler(WebSocketHandler):
    def open(self,sensorId):
        if sensorId!=None and persudoDatabase.database.sensors.__contains__(sensorId):
            self.write_message('sensor, welcome to publish.')
        else:
            persudoDatabase.database.users.add(self)
            self.write_message('user, welcome to subscribe.')

    def on_message(self, message):
        for u in persudoDatabase.database.users:
            u.write_message(message)
    
    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
            (r"/", IndexHandler),
            (r"/sensor/(.*)", SensorHandler),
            (r"/register/(.*)", RegisterHandler),
            (r"/admin", AdminHandler),
        ],
        static_path = os.path.join(os.path.dirname(__file__), "static"),
        template_path = os.path.join(os.path.dirname(__file__), "template"),
        debug = True
        )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()