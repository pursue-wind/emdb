from tornado.web import url

from handlers.emmai_handler import CountCompanyMovies
from handlers.movie_extra_info import MovieAlternativeTitles, MovieCredits, MovieReleaseDates, MovieImages, MovieVideos, \
    MovieTranslations, GetMoviRealeseCertifications
from handlers.movie_handler import *
from handlers.tv_extra_info import TVAlternativeTitles, TVCredits, TVReleaseDates, TVImages, TVVideos, TVTranslations
from handlers.tv_handler import SearchCompanyTV, GetTVEpisodes, SearchTV, AddTV

MOVIE_ROUTE = [
    ("/api/emdb/movie/search", SearchMovieOnline),
    ("/api/movie/search", SearchMovie),
    ("/api/movie/add", AddMovie),
    ("/api/movie/alternative_titles", MovieAlternativeTitles),
    ("/api/movie/credits", MovieCredits),
    ("/api/movie/release_dates", MovieReleaseDates),
    ("/api/movie/images", MovieImages),
    ("/api/movie/videos", MovieVideos),
    ("/api/movie/translations", MovieTranslations),
    ("/api/movie/certifications", GetMoviRealeseCertifications),

    ("/api/tv/search", SearchTV),
    ("/api/tv/add", AddTV),
    ("/api/tv/alternative_titles", TVAlternativeTitles),
    ("/api/tv/credits", TVCredits),
    ("/api/tv/release_dates", TVReleaseDates),
    ("/api/tv/images", TVImages),
    ("/api/tv/videos", TVVideos),
    ("/api/tv/translations", TVTranslations),
    ("/api/tv/certifications", GetMoviRealeseCertifications),
    ("/api/tv/episodes", GetTVEpisodes)

]


COMPANY_ROUTE = [
    ("/api/company/search", SearchCompany),
    ("/api/company/movies", SearchCompanyMovies),
    ("/api/company/tv", SearchCompanyTV),
]


EMMAI_ROUTE = [
    ("/api/media/count", CountCompanyMovies)
]