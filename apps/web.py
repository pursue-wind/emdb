from tornado.web import Application

from apps.config.config import cfg
from apps.handlers.movie import MovieHandler
from apps.handlers.tv import TVHandler


def make_app(session_factory):
    return Application([
        (r"/api/emdb/movie/([0-9]+)", MovieHandler, dict(session_factory=session_factory)),
        (r"/api/emdb/tv/([0-9]+)", TVHandler, dict(session_factory=session_factory)),
    ], debug=cfg.DEBUG)
