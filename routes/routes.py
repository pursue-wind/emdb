from tornado.web import url

from handlers.movie_extra_info import MovieAlternativeTitles, MovieCredits, MovieReleaseDates, MovieImages, MovieVideos, \
    MovieTranslations, GetMoviRealeseCertifications
from handlers.movie_handler import SearchMovie, SearchCompany, AddMovie, SearchCompanyMovies
from handlers.tv_handler import SearchCompanyTV, GetTVEpisodes

MOVIE_ROUTE = [
    ("/api/movie/search", SearchMovie),
    ("/api/movie/add", AddMovie),
    ("/api/movie/alternative_titles", MovieAlternativeTitles),
    ("/api/movie/credits", MovieCredits),
    ("/api/movie/release_dates", MovieReleaseDates),
    ("/api/movie/images", MovieImages),
    ("/api/movie/videos", MovieVideos),
    ("/api/movie/translations", MovieTranslations),
    ("/api/movie/certifications", GetMoviRealeseCertifications),

    ("/api/tv/search", SearchMovie),
    ("/api/tv/add", AddMovie),
    ("/api/tv/alternative_titles", MovieAlternativeTitles),
    ("/api/tv/credits", MovieCredits),
    ("/api/tv/release_dates", MovieReleaseDates),
    ("/api/tv/images", MovieImages),
    ("/api/tv/videos", MovieVideos),
    ("/api/tv/translations", MovieTranslations),
    ("/api/tv/certifications", GetMoviRealeseCertifications),
    ("/api/tv/episodes", GetTVEpisodes)

]


COMPANY_ROUTE = [
    ("/api/company/search", SearchCompany),
    ("/api/company/movies", SearchCompanyMovies),
    ("/api/company/tv", SearchCompanyTV),

]