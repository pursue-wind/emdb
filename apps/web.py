from tornado.web import Application

from apps.config.config import cfg
from apps.handlers.movie import *
from apps.handlers.tv import TVHandler


def make_app(session_factory):
    return Application([
        (r"/api/emdb/movie/([0-9]+)", MovieHandler, dict(session_factory=session_factory)),
        (r"/api/emdb/tv/([0-9]+)", TVHandler, dict(session_factory=session_factory)),

        # 兼容之前的接口
        (r"/api/movie/images", MovieImagesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/translations", MovieTranslationsHandler, dict(session_factory=session_factory)),
        (r"/api/movie/alternative_titles", MovieAlternativeTitlesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/credits", MovieCreditsHandler, dict(session_factory=session_factory)),
        (r"/api/movie/release_dates", MovieReleaseDatesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/videos", MovieVideosHandler, dict(session_factory=session_factory)),
    ], debug=cfg.DEBUG)
