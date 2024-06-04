from tornado import gen

from db.pgsql.enums.enums import get_key_by_value, GenresType
from db.pgsql.movie_key_words import query_movie_keywords
from db.pgsql.movies import query_movie_by_name, query_movie_by_tmdb_id, query_movie_by_company_id
from db.pgsql.production_company import query_company_by_name, query_company_by_ids
from handlers.base_handler import BaseHandler
from service.fetch_moive_info import fetch_movie_info
from service.search_online import search_company_movies, search_movie_by_name
from db.pgsql.enums.enums import SourceType


class SearchMovieOnline(BaseHandler):
    """
    search by name or tmdb movie id
    :returns movies
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('movie_name', 'lang', 'page')
        movie_name = args.movie_name
        lang = args.lang
        page = args.page
        # tmdb_movie_id = args.tmdb_movie_id
        yield self.check_auth()

        res = yield search_movie_by_name(movie_name, lang=lang, page=page)
        self.success(data=res['data'])


class SearchMovie(BaseHandler):
    """
    search by name or tmdb movie id
    :returns movies
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('movie_name')
        movie_name = args.movie_name
        # tmdb_movie_id = args.tmdb_movie_id
        yield self.check_auth()
        result = yield query_movie_by_name(movie_name)
        data = result.get('data', None)
        if not data:
            self.success(data=dict())
        movies = list()
        for mv in data["movies"]:
            if mv["release_date"] is not None:
                mv["release_date"] = mv['release_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                mv["release_date"] = None
            mv["vote_average"] = float(mv["vote_average"])
            mv["popularity"] = float(mv["popularity"])
            movies.append(mv)
            # get genres
            genres_ids = mv["genres"]
            genres_value = []
            for gen in genres_ids:
                value = get_key_by_value(GenresType, gen)
                genres_value.append(value)
            mv["genres"] = genres_value
            production_company_ids = mv["production_companies"]
            production_companies = yield query_company_by_ids(production_company_ids)
            mv["production_companies"] = production_companies["data"]["companies"]
            keywords_list = yield query_movie_keywords(mv["id"])
            mv["keywords"] = keywords_list.get("data")
        self.success(data=dict(movies=movies))


class AddMovie(BaseHandler):
    """
    add movie by tmdb movie id
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_movie_id')
        tmdb_movie_id = args.tmdb_movie_id
        yield self.check_auth()
        res = yield query_movie_by_tmdb_id(tmdb_movie_id, SourceType.Movie.value)
        if res['status'] == 0:
            if res["data"]["movie_info"]:
                movie_id = res["data"]["movie_info"]["id"]
                self.success(msg="Already Exist!", data=dict(movie_id=movie_id))
        ok, movie_id = yield fetch_movie_info(tmdb_movie_id)
        if ok:
            self.success(data=dict(movie_id=movie_id))
        else:
            self.fail(405)


class SearchCompany(BaseHandler):
    """
    search company by name
    """

    # @tornado_swagger.api_doc("API Endpoint Summary", "API Endpoint Description")
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('company_name')
        company_name = args.company_name
        yield self.check_auth()
        result = yield query_company_by_name(company_name)
        # print(f"re:{result}")
        data = result.get('data', None)
        if not data:
            self.success(data=dict())

        self.success(data=dict(companies=data["companies"]))


class SearchCompanyMoviesOnTmdb(BaseHandler):
    """
    search all movies of a company by company id in tmdb
    :returns movies list
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_company_id')
        tmdb_company_id = args.tmdb_company_id
        yield self.check_auth()
        res = yield search_company_movies(tmdb_company_id)
        if res["code"] != 0:
            self.success(data=dict(movies=[]))
        movies = res["data"]["results"]
        self.success(data=dict(movies=movies))


class SearchCompanyMovies(BaseHandler):
    """
    search all movie of company
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_json_arguments('tmdb_company_id', page_num=1, page_size=10, movie_name=None)
        tmdb_company_id = args.tmdb_company_id
        if not all([tmdb_company_id]):
            self.fail(402)
        print(args)
        # movie_name = args.movie_name
        yield self.check_auth()
        result = yield query_movie_by_company_id(tmdb_company_id, SourceType.Movie.value, movie_name=args.movie_name,
                                                 page_num=args.page_num,
                                                 page_size=args.page_size)
        print(result)
        if "status" in result and result["status"] != 0:
            self.fail(1)
        data = result.get('data', None)
        # if not data:
        #     self.success(data=dict())
        movies = list()
        for mv in data["movies"]:
            if mv['release_date'] is not None:
                release_date = mv['release_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                release_date = None
            mv["release_date"] = release_date
            mv["vote_average"] = float(mv["vote_average"])
            mv["popularity"] = float(mv["popularity"])
            movies.append(mv)
            # get genres
            genres_ids = mv["genres"]
            genres_value = []
            for gen in genres_ids:
                value = get_key_by_value(GenresType, gen)
                genres_value.append(value)
            mv["genres"] = genres_value
            production_company_ids = mv["production_companies"]
            production_companies = yield query_company_by_ids(production_company_ids)
            mv["production_companies"] = production_companies["data"]["companies"]
            keywords_list = yield query_movie_keywords(mv["id"])
            mv["keywords"] = keywords_list.get("data")
        self.success(data=dict(page_num=args.page_num,
                               page_size=args.page_size,
                               total=data.get('total', 0),
                               movies=movies))
