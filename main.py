import logging
import sys

import tornado.web
from tornado.log import access_log, app_log
from lib.logger import init_log
from routes import ROUTES as routes
from config import CFG as cfg
from db.mongo import init_mongo
from lib.generate import get_appkey, create_token, get_appsecret
def log_function(handler):
    """
    日志处理
    :param handler:
    :return:
    """
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    status = handler.get_status()
    summary = handler._request_summary()
    log_method(f'{request_time:6.2f}ms {status} {summary}')


class Application(tornado.web.Application):
    def __init__(self):
        super(Application, self).__init__(handlers=routes, log_function=log_function, **cfg.application)
        init_log(log_name="main")
        init_mongo()
        # cfg.show()


if __name__ == "__main__":
    app = Application()
    app.listen(cfg.server.port)
    app_log.info(f"servive start listening on {cfg.server.host}:{cfg.server.port}")
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()

