from tornado import gen
from tornado_swagger.model import register_swagger_model

from db.pgsql.enums.enums import get_key_by_value, GenresType
from db.pgsql.movie_key_words import query_movie_keywords
from db.pgsql.movies import query_movie_by_name, query_movie_by_tmdb_id, query_movie_by_company_id, \
    query_movie_by_tmdb_ids, exist_movie_by_tmdb_id
from db.pgsql.production_company import query_company_by_name, query_company_by_ids
from handlers.auth_decorators import auth
from handlers.base_handler import BaseHandler
from service.fetch_moive_info import fetch_movie_info
from service.fetch_tv_series_info import get_tv_detail
from service.search_online import search_company_movies
from db.pgsql.enums.enums import SourceType
from service.search_service import SearchService


class MovieHandler(BaseHandler):

    @auth
    async def post(self, *_args, **_kwargs):
        """
        数据入库：必传，电影类型：movie，电视类型：tv
        """

        tmdb_id, lang, media_type, tv_season_id, cover = self.parse_body('id', 'lang', 'media_type',
                                                                         'tv_season_id', 'cover',
                                                                         required=['id', 'lang', 'media_type'])
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')

        if not lang:
            lang = 'zh'

        is_movie_type = media_type == 'movie'
        if not is_movie_type and not tv_season_id:
            self.fail(status=400, msg='media_type param err')

        # 强制覆盖的话，不检查是否已存在数据库
        if not cover:
            exist_id = await exist_movie_by_tmdb_id(tmdb_id,
                                                    SourceType.Movie.value if is_movie_type else SourceType.Tv.value)
            if exist_id:
                self.success(data=list())

        # get_tv_detail_filter_season(tmdb_series_id_list[i], season_id_list[i], company_id)
        if is_movie_type:
            r = await fetch_movie_info(tmdb_id, lang=lang)
            self.success(data=tmdb_id)
        else:
            r = await get_tv_detail(tmdb_id, lang=lang, season_id=[tv_season_id])
            self.success(data=tmdb_id)


class MovieMultiHandler(BaseHandler):

    @auth
    async def post(self, *_args, **_kwargs):
        """
        数据入库：必传，电影类型：movie，电视类型：tv
        """

        tmdb_movie_ids, media_type, tv_series_id = self.parse_body('ids', 'media_type', 'tv_series_id',
                                                                   required=['media_type'])
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')
        is_movie_type = media_type == 'movie'
        exist_ids = await query_movie_by_tmdb_ids(tmdb_movie_ids,
                                                  SourceType.Movie.value if is_movie_type else SourceType.Tv.value)

        # get_tv_detail_filter_season(tmdb_series_id_list[i], season_id_list[i], company_id)
        need_import = set(tmdb_movie_ids) - exist_ids['data']
        if is_movie_type:
            for id in need_import:
                r = await fetch_movie_info(id)
        else:
            r = await get_tv_detail(tv_series_id, season_id=need_import)

        self.success(data=list(need_import))


@register_swagger_model
class Discover(BaseHandler):
    @auth
    async def get(self, *_args, **_kwargs):
        """
         ---
         summary: Discover
         description: 电影电视推荐接口
         produces:
         - application/json
         parameters:
         -   name: lang
             description: lang
             type: string
         -   name: page
             description: page
             type: integer
         -   name: media_type
             description: 必传，电影类型：movie，电视类型：tv
             required: true
             type: integer
         -   name: include_adult
             description: 是否包含成人内容
             required: false
             type: boolean
             default: true
         responses:
             200:
               description: list of result
         """

        lang, page, media_type, include_adult = self.parse_form('lang', 'page', 'media_type', 'include_adult')
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')
        res = await SearchService().discover(lang=lang, page=page, media_type=media_type, include_adult=include_adult)
        self.success(data=res)


@register_swagger_model
class TMDBTVDetails(BaseHandler):
    @auth
    async def get(self, *_args, **_kwargs):
        """
        ---
        summary: TVDetails
        description: 通过series_id 获取 TVDetails
        produces:
          - application/json
        parameters:
          - name: series_id
            description: series_id
            type: integer
          - name: lang
            description: lang
            type: string
         """
        lang, series_id = self.parse_form('lang', 'series_id')
        res = await SearchService().tv_detail_by_series_id(lang=lang, series_id=series_id)
        self.success(data=res)


@register_swagger_model
class TMDBSearch(BaseHandler):

    @auth
    async def get(self, *_args, **_kwargs):
        """
        ---
        summary: Discover
        description: 电影电视搜索接口
        produces:
          - application/json
        parameters:
          - name: name
            description: 通过电影/电视名称搜索
            type: string
          - name: lang
            description: lang
            type: string
          - name: page
            description: page
            required: true
            type: integer
          - name: media_type
            description: 必传，电影类型：movie，电视类型：tv
            required: true
            type: integer
          - name: include_adult
            description: 是否包含成人内容
            required: false
            type: boolean
            default: true
          - name: t_id
            description: tmdb_id / tmdb_series_id
            type: integer
        responses:
          200:
            description: list of result
         """
        name, lang, page, media_type, include_adult, \
            t_id = self.parse_form('name', 'lang', 'page', 'media_type', 'include_adult', 't_id',
                                   required=['media_type'])
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')
        if name and t_id:
            self.fail(status=400, msg='only name or id')

        res = await SearchService().search(name, lang=lang, page=page, media_type=media_type, t_id=t_id)
        self.success(data=res)


class SearchMovie(BaseHandler):
    """
    search by name or tmdb movie id
    :returns movies
    """

    @auth
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        movie_name = self.parse_form('movie_name', required=['movie_name'])

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

    @auth
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        tmdb_movie_id = self.parse_form('tmdb_movie_id', require_all=True)

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
    @auth
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('company_name')
        company_name = args.company_name

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

    @auth
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_company_id')
        tmdb_company_id = args.tmdb_company_id

        res = yield search_company_movies(tmdb_company_id)
        if res["code"] != 0:
            self.success(data=dict(movies=[]))
        movies = res["data"]["results"]
        self.success(data=dict(movies=movies))


class SearchCompanyMovies(BaseHandler):
    """
    search all movie of company
    """

    @auth
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_json_arguments('tmdb_company_id', page_num=1, page_size=10, movie_name=None)
        tmdb_company_id = args.tmdb_company_id
        if not all([tmdb_company_id]):
            self.fail(402)
        print(args)
        # movie_name = args.movie_name

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
