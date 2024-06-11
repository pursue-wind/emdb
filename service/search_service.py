import logging

from db.pgsql.movies_dao import exist_ids_by_tmdb_ids
from db.pgsql.tv_dao import exist_ids_by_tmdb_series_ids
from service.fetch_moive_info import Tmdb


class SearchService:
    def __init__(self):
        self.t = Tmdb
        self.movie_media_type_check_func = (lambda media_type: media_type is not None and media_type == "movie")
        self.tv_media_type_check_func = (lambda media_type: media_type is not None and media_type == "tv")

    def data_convent(self, d: dict, exist_ids: set = None) -> dict:
        def get_full_image_path(key: str) -> str:
            return self.t.IMAGE_BASE_URL + d[key] if key in d and d[key] else None

        d["poster_path"] = get_full_image_path("poster_path")
        d["backdrop_path"] = get_full_image_path("backdrop_path")

        if exist_ids is not None:
            d["exist"] = d.get("id") in exist_ids

        return d

    async def get_exist_ids(self, is_movie_type, movies) -> set:
        ids = list(map(lambda d: d['id'], movies))
        check_func = exist_ids_by_tmdb_ids if is_movie_type else exist_ids_by_tmdb_series_ids
        return await check_func(ids)

    async def discover(self, lang='en', page=1, media_type="movie", include_adult=True):
        is_movie_type = self.movie_media_type_check_func(media_type)
        search_method = (self.t.discover.movie if is_movie_type else self.t.discover.tv)
        result = search_method(language=lang, page=page, include_adult=include_adult)
        # logging.info(f" results:{result}")
        media_list = result.get("results", [])
        exist_ids = await self.get_exist_ids(is_movie_type, media_list)
        data = list(map(lambda d: self.data_convent(d, exist_ids), media_list))
        return dict(page_num=int(page),
                    page_size=20,
                    total=result.get('total_results', 0),
                    data=data)

    async def search(self, name, lang='en', page=1, media_type="movie", include_adult=True, t_id=None):
        is_movie_type = self.movie_media_type_check_func(media_type)
        if t_id:
            res = self.t.tmdb.Movies(t_id).info(language=lang) if is_movie_type else self.t.tmdb.TV(t_id).info(
                language=lang)
            return dict(page_num=int(page),
                        page_size=20,
                        total=1 if res else 0,
                        data=[self.data_convent(res)])
        search_method = self.t.search.movie if is_movie_type else self.t.search.tv

        result = search_method(language=lang, query=name, page=page, include_adult=include_adult)
        # logging.info(f"search results:{result}")
        media_list = result.get("results", [])

        exist_ids = await self.get_exist_ids(is_movie_type, media_list)
        data = list(map(lambda d: self.data_convent(d, exist_ids), media_list))

        return dict(page_num=int(page),
                    page_size=20,
                    total=result.get('total_results', 0),
                    data=data)

    async def tv_detail_by_series_id(self, series_id, lang='en'):
        return self.t.tmdb.TV(series_id).info(language=lang)
