import os

import tornado.web
from tornado.log import access_log, app_log

from db.pgsql.mysql_models import init_db
# from db.pgsql.base import init_db
from lib.logger import init_log
from routes import ROUTES as routes
from config import CFG as cfg
from tornado_swagger.setup import setup_swagger


def log_function(handler):
    """
    log handler
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

        setup_swagger(
            routes=routes,
            swagger_url="/docs",
            api_base_url="/api",
            description="",
            api_version="1.0.0",
            title="EMDB API",
        )

        super(Application, self).__init__(handlers=routes, log_function=log_function, **cfg.application)
        init_log(log_name="main")

        # cfg.show()
        init_db()


if __name__ == "__main__":
    app = Application()
    app.listen(cfg.server.port)
    app_log.info("*"*40)
    app_log.info(f"servive start listening on {cfg.server.host}:{cfg.server.port}")
    _ENV = os.getenv('ENV')
    app_log.info(f"current ENV：{_ENV}")
    app_log.info("*"*40)
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()

