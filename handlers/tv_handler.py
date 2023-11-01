from db.pgsql.movies import query_movie_by_company_id
from db.pgsql.tv_episodes import get_tv_episodes_list
from db.pgsql.tv_seasons import get_tv_season_params
from handlers.base_handler import BaseHandler
from tornado import gen
from db.pgsql.enums.enums import get_key_by_value, GenresType
from db.pgsql.production_company import query_company_by_ids
from db.pgsql.movie_key_words import query_movie_keywords
from db.pgsql.enums.enums import SourceType


class SearchCompanyTV(BaseHandler):
    @gen.coroutine
    def post(self, *_args, **_kwargs):

        args = self.parse_form_arguments('tmdb_company_id', page_num=1, page_size=10, tv_name=None)
        tmdb_company_id = args.tmdb_company_id
        page_num = int(args.page_num)
        page_size = int(args.page_size)
        if not all([tmdb_company_id]):
            self.fail(402)
        print(args)
        yield self.check_auth()
        result = yield query_movie_by_company_id(tmdb_company_id, SourceType.Tv.value, movie_name=args.tv_name,
                                                 page_num=page_num,
                                                 page_size=page_size)
        print(result)
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
            season_name = yield get_tv_season_params(tv['tmdb_id'])
            tv['name'] = season_name['data']['name']
            tv['episode_count'] = season_name['data']['episode_count']
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

        self.success(data=dict(episodes_list=episodes,total=data.get('total')))
