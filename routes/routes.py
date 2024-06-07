import tornado
from tornado.web import url

from handlers.emmai_handler import CountCompanyMovies
from handlers.movie_extra_info import MovieAlternativeTitles, MovieCredits, MovieReleaseDates, MovieImages, MovieVideos, \
    MovieTranslations, GetMoviRealeseCertifications
from handlers.movie_handler import *
from handlers.tv_extra_info import TVAlternativeTitles, TVCredits, TVReleaseDates, TVImages, TVVideos, TVTranslations
from handlers.tv_handler import SearchCompanyTV, GetTVEpisodes, SearchTV, AddTV

MOVIE_ROUTE = [
    tornado.web.url("/api/emdb/tv/details", TMDBTVDetails),
    tornado.web.url("/api/emdb/discover", Discover),
    tornado.web.url("/api/emdb/search", TMDBSearch),
    tornado.web.url("/api/emdb/save", MovieHandler),
    tornado.web.url("/api/movie/search", SearchMovie),
    tornado.web.url("/api/movie/add", AddMovie),
    tornado.web.url("/api/movie/alternative_titles", MovieAlternativeTitles),
    tornado.web.url("/api/movie/credits", MovieCredits),
    tornado.web.url("/api/movie/release_dates", MovieReleaseDates),
    tornado.web.url("/api/movie/images", MovieImages),
    tornado.web.url("/api/movie/videos", MovieVideos),
    tornado.web.url("/api/movie/translations", MovieTranslations),
    tornado.web.url("/api/movie/certifications", GetMoviRealeseCertifications),

    tornado.web.url("/api/tv/search", SearchTV),
    tornado.web.url("/api/tv/add", AddTV),
    tornado.web.url("/api/tv/alternative_titles", TVAlternativeTitles),
    tornado.web.url("/api/tv/credits", TVCredits),
    tornado.web.url("/api/tv/release_dates", TVReleaseDates),
    tornado.web.url("/api/tv/images", TVImages),
    tornado.web.url("/api/tv/videos", TVVideos),
    tornado.web.url("/api/tv/translations", TVTranslations),
    tornado.web.url("/api/tv/certifications", GetMoviRealeseCertifications),
    tornado.web.url("/api/tv/episodes", GetTVEpisodes)

]


COMPANY_ROUTE = [
   tornado.web.url("/api/company/search", SearchCompany),
   tornado.web.url("/api/company/movies", SearchCompanyMovies),
   tornado.web.url("/api/company/tv", SearchCompanyTV),
]


EMMAI_ROUTE = [
    tornado.web.url("/api/media/count", CountCompanyMovies)
]