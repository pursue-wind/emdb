from db.pgsql.movies import query_movie_by_company_id, query_movie_by_name, query_movie_by_tmdb_id
from db.pgsql.tv_episodes import get_tv_episodes_list
from db.pgsql.tv_seasons import get_tv_season_params
from db.pgsql.tv_series_additional import get_tv_additional_info
from handlers.base_handler import BaseHandler
from tornado import gen
from db.pgsql.enums.enums import get_key_by_value, GenresType
from db.pgsql.production_company import query_company_by_ids, query_company_by_name
from db.pgsql.movie_key_words import query_movie_keywords
from db.pgsql.enums.enums import SourceType
from service.fetch_moive_info import fetch_movie_info
from service.search_online import search_company_movies


class SearchTV(BaseHandler):
    """
    search by name or tmdb tv id
    :returns tvs
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_name')
        tv_name = args.tv_name
        # tmdb_tv_id = args.tmdb_tv_id
        yield self.check_auth()
        result = yield query_movie_by_name(tv_name)
        data = result.get('data', None)
        if not data:
            self.success(data=dict())
        tvs = list()
        for mv in data["movies"]:
            mv["release_date"] = mv['release_date'].strftime('%Y-%m-%d %H:%M:%S')
            mv["vote_average"] = float(mv["vote_average"])
            mv["popularity"] = float(mv["popularity"])
            tvs.append(mv)
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
        self.success(data=dict(tv=tvs))


class AddTV(BaseHandler):
    """
    add tv by tmdb tv id
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_tv_id')
        tmdb_tv_id = args.tmdb_tv_id
        yield self.check_auth()
        res = yield query_movie_by_tmdb_id(tmdb_tv_id, SourceType.Tv.value)
        if res['status'] == 0:
            if res["data"]["tv_info"]:
                tv_id = res["data"]["tv_info"]["id"]
                self.success(msg="Already Exist!", data=dict(tv_id=tv_id))
        ok, tv_id = yield fetch_movie_info(tmdb_tv_id)
        if ok:
            self.success(data=dict(tv_id=tv_id))
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


class SearchCompanyTVsOnTmdb(BaseHandler):
    """
    search all tvs of a company by company id in tmdb
    :returns tvs list
    """

    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_company_id')
        tmdb_company_id = args.tmdb_company_id
        yield self.check_auth()
        res = yield search_company_movies(tmdb_company_id)
        if res["code"] != 0:
            self.success(data=dict(tvs=[]))
        tvs = res["data"]["results"]
        self.success(data=dict(tvs=tvs))


class SearchCompanyTV(BaseHandler):
    @gen.coroutine
    def post(self, *_args, **_kwargs):

        args = self.parse_json_arguments('tmdb_company_id', page_num=1, page_size=10, tv_name=None)
        tmdb_company_id = args.tmdb_company_id
        page_num = int(args.page_num)
        page_size = int(args.page_size)
        if not all([tmdb_company_id]):
            self.fail(402)
        yield self.check_auth()
        result = yield query_movie_by_company_id(tmdb_company_id, SourceType.Tv.value, movie_name=args.tv_name,
                                                 page_num=page_num,
                                                 page_size=page_size)

        if "status" in result and result["status"] != 0:
            self.fail(1)
        data = result.get('data', None)
        tvs = list()
        for tv in data['movies']:
            if tv['release_date'] is not None:
                release_date = tv['release_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                release_date = None
            tv['release_date'] = release_date
            tv['vote_average'] = float(tv['vote_average'])
            tv['popularity'] = float(tv['popularity'])
            genres_ids = tv['genres']
            genres_value = []
            for ge in genres_ids:
                value = get_key_by_value(GenresType, ge)
                genres_value.append(value)
            tv['genres'] = genres_value
            production_company_ids = tv['production_companies']
            production_companies = yield query_company_by_ids(production_company_ids)
            tv['production_companies'] = production_companies['data']['companies']
            keyword_list = yield query_movie_keywords(tv['id'])
            tv['keywords'] = keyword_list.get('data')
            result = yield get_tv_season_params(tv['tmdb_id'])
            season_detail = result.get('data')
            if season_detail['air_date'] is not None:
                season_detail['air_date'] = season_detail['air_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                season_detail['air_date'] = None

            tv['episode_detail'] = season_detail
            result = yield get_tv_additional_info(tv['tmdb_series_id'])

            additional_info = result.get('data')['data']
            if additional_info['first_air_date'] is not None:
                first_air_date = additional_info['first_air_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                first_air_date = None
            additional_info['first_air_date'] = first_air_date

            if additional_info['last_air_date'] is not None:
                last_air_date = additional_info['last_air_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_air_date = None
            additional_info['last_air_date'] = last_air_date
            del additional_info['external_ids']
            tv['additional_info'] = additional_info

            tvs.append(tv)
        self.success(data=dict(page_num=page_num,
                               page_size=page_size,
                               total=data.get('total', 0),
                               tvs=tvs))


class GetTVEpisodes(BaseHandler):
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_season_id')
        tmdb_season_id = args.tmdb_season_id
        result = yield get_tv_episodes_list(tmdb_season_id)
        data = result.get('data')
        episodes = []
        for episode in data['episodes_list']:
            if episode['air_date'] is not None:
                air_date = episode['air_date'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                air_date = None
            episode['air_date'] = air_date
            episode['vote_average'] = float(episode['vote_average'])
            episodes.append(episode)

        self.success(data=dict(episodes_list=episodes, total=data.get('total')))
