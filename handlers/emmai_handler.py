from db.pgsql.enums.enums import SourceType
from db.pgsql.movies import count_movies_of_company, count_movies_of_all_company
from handlers.auth_decorators import auth
from handlers.base_handler import BaseHandler
from tornado import gen


class CountCompanyMovies(BaseHandler):
    """
    return movie and tv shows number of company
    """
    @auth
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        movie_count_res = yield count_movies_of_all_company(SourceType.Movie.value)
        print(movie_count_res)
        if "status" in movie_count_res and movie_count_res["status"] != 0:
            self.fail(1)
        movie_count = movie_count_res.get('data', 0)

        tv_count_res = yield count_movies_of_all_company(SourceType.Tv.value)
        print(movie_count_res)
        if "status" in tv_count_res and tv_count_res["status"] != 0:
            self.fail(1)
        tv_count = tv_count_res.get('data', 0)

        self.success(data=dict(movie_count=movie_count["total_count"], tv_count=tv_count["total_count"]))
