from db.pgsql.movies import query_movie_by_company_id
from handlers.base_handler import BaseHandler
from tornado import gen
from db.pgsql.enums.enums import get_key_by_value, GenresType
from db.pgsql.production_company import query_company_by_ids
from db.pgsql.movie_key_words import query_movie_keywords
from db.pgsql.enums.enums import SourceType


class SearchCompanyTV(BaseHandler):
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        print(12323413451345234534523452345)

        args = self.parse_form_arguments('tmdb_company_id', page_num=1, page_size=10, tv_name=None)
        tmdb_company_id = args.tmdb_company_id
        if not all([tmdb_company_id]):
            self.fail(402)
        print(args)
        yield self.check_auth()
        result = yield query_movie_by_company_id(tmdb_company_id, SourceType.Tv.value, movie_name=args.tv_name,
                                                 page_num=args.page_num,
                                                 page_size=args.page_size)
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
            tvs.append(tv)
        self.success(data=dict(page_num=args.page_num,
                               page_size=args.page_size,
                               total=data.get('total', 0),
                               tvs=tvs))
