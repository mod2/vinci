from werkzeug.contrib.fixers import ProxyFix
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from web import app

app.wsgi_app = ProxyFix(app.wsgi_app)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(5002)
IOLoop.instance().start()
