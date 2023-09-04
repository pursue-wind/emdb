from tornado.web import url

from handlers.movie_extra_info import MovieAlternativeTitles, MovieCredits, MovieReleaseDates, MovieImages, MovieVideos, \
    MovieTranslations, GetMoviRealeseCertifications
from handlers.movie_handler import SearchMovie, SearchCompany, AddMovie, SearchCompanyMovies

MOVIE_ROUTE = [
    ("/api/movie/search", SearchMovie),
    ("/api/movie/add", AddMovie),
    ("/api/movie/alternative_titles", MovieAlternativeTitles),
    ("/api/movie/credits", MovieCredits),
    ("/api/movie/release_dates", MovieReleaseDates),
    ("/api/movie/images", MovieImages),
    ("/api/movie/videos", MovieVideos),
    ("/api/movie/translations", MovieTranslations),
    ("/api/movie/certifications", GetMoviRealeseCertifications)
]


COMPANY_ROUTE = [
    ("/api/company/search", SearchCompany),
    ("/api/company/movies", SearchCompanyMovies),

]