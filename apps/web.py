from tornado.web import Application

import config
from apps.handlers.movie import *
from apps.handlers.movie_old import *
from apps.handlers.tv import TVHandler


def make_app(session_factory):
    return Application([
        (r"/api/emdb/movie/([0-9]+)", MovieHandler, dict(session_factory=session_factory)),
        (r"/api/emdb/tv/([0-9]+)", TVHandler, dict(session_factory=session_factory)),

        # 兼容之前的接口
        (r"/api/movie/images", MovieImagesHandler, dict(session_factory=session_factory)),
        (r"/api/tv/images", TVImagesHandler, dict(session_factory=session_factory)),
        (r"/api/tv/episodes", TVEpisodesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/translations", MovieTranslationsHandler, dict(session_factory=session_factory)),
        (r"/api/tv/translations", TVTranslationsHandler, dict(session_factory=session_factory)),
        (r"/api/movie/alternative_titles", MovieAlternativeTitlesHandler, dict(session_factory=session_factory)),
        (r"/api/tv/alternative_titles", TVAlternativeTitlesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/credits", MovieCreditsHandler, dict(session_factory=session_factory)),
        (r"/api/tv/credits", TVCreditsHandler, dict(session_factory=session_factory)),
        (r"/api/movie/release_dates", MovieReleaseDatesHandler, dict(session_factory=session_factory)),
        (r"/api/tv/release_dates", TVReleaseDatesHandler, dict(session_factory=session_factory)),
        (r"/api/movie/videos", MovieVideosHandler, dict(session_factory=session_factory)),
        (r"/api/tv/videos", TVVideosHandler, dict(session_factory=session_factory)),
        (r"/api/media/count", CountCompanyMovies, dict(session_factory=session_factory)),

        ("/api/company/movies", SearchCompanyMovies, dict(session_factory=session_factory)),
        ("/api/company/tv", SearchCompanyTV, dict(session_factory=session_factory)),
        ("/api/emdb/tv/details", TMDBTVDetails, dict(session_factory=session_factory)),
        ("/api/emdb/discover", DiscoverHandler, dict(session_factory=session_factory)),
        ("/api/emdb/search", TMDBSearch, dict(session_factory=session_factory)),
        ("/api/emdb/", Movie2Handler, dict(session_factory=session_factory)),
    ], debug=config.settings.DEBUG)
