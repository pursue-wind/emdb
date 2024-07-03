from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.domain.base import movie_upload_progress, tv_upload_progress, tv_upload_progress_build_key
from apps.domain.models import TMDBMovie, TMDBTV, TMDBTVSeason
from apps.services.base import BaseService
import tmdbsimple as tmdb


class SearchService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.movie_media_type_check_func = (lambda media_type: media_type is not None and media_type == "movie")
        self.tv_media_type_check_func = (lambda media_type: media_type is not None and media_type == "tv")

    def data_convent(self, d: dict, exist_ids: set = None) -> dict:
        def get_full_image_path(key: str) -> str:
            return self.IMAGE_BASE_URL + d[key] if key in d and d[key] else None

        d["poster_path"] = get_full_image_path("poster_path")
        d["backdrop_path"] = get_full_image_path("backdrop_path")

        if exist_ids is not None:
            d["exist"] = d.get("id") in exist_ids

        return d

    def data_import_check(self, d: dict, is_movie_type: bool, series_id=None) -> dict:
        if is_movie_type:
            d['is_importing'] = d.get('id', -1) in movie_upload_progress
        else:
            if series_id is not None:
                d['is_importing'] = tv_upload_progress_build_key(series_id, d.get('id', -1)) in tv_upload_progress

        return d

    async def get_exist_ids(self, is_movie_type, movies) -> set:
        async with self.session.begin():
            ids = list(map(lambda d: d['id'], movies))
            if is_movie_type:
                result = await self.session.execute(select(TMDBMovie.id).where(TMDBMovie.id.in_(ids)))
                e_ids = result.scalars().all()
                return set(e_ids)
            else:
                result = await self.session.execute(select(TMDBTV.id).where(TMDBTV.id.in_(ids)))
                e_ids = result.scalars().all()
                return set(e_ids)

    async def discover(self, lang='en', page=1, media_type="movie", include_adult=True):
        is_movie_type = self.movie_media_type_check_func(media_type)
        discover = tmdb.discover.Discover()
        search_method = (discover.movie if is_movie_type else discover.tv)
        result = search_method(language=lang, page=page, include_adult=include_adult)
        # logging.info(f" results:{result}")
        media_list = result.get("results", [])
        exist_ids = await self.get_exist_ids(is_movie_type, media_list)
        data = list(map(lambda d: self.data_convent(d, exist_ids), media_list))
        data = list(map(lambda d: self.data_import_check(d, is_movie_type=is_movie_type, series_id=None), data))
        return dict(page_num=int(page),
                    page_size=20,
                    total=result.get('total_results', 0),
                    data=data)

    async def search(self, name, lang='en', page=1, media_type="movie", include_adult=True, t_id=None):
        is_movie_type = self.movie_media_type_check_func(media_type)
        if t_id:
            try:
                res = tmdb.Movies(t_id).info(language=lang) if is_movie_type else tmdb.TV(t_id).info(
                    language=lang)
                return dict(page_num=int(page),
                            page_size=20,
                            total=1 if res else 0,
                            data=[self.data_convent(res)])
            except Exception as e:
                return dict(page_num=int(page),
                            page_size=20,
                            total=0,
                            data=[])
        search_method = tmdb.search.Search().movie if is_movie_type else tmdb.search.Search().tv

        result = search_method(language=lang, query=name, page=page, include_adult=include_adult)
        # logging.info(f"search results:{result}")
        media_list = result.get("results", [])

        exist_ids = await self.get_exist_ids(is_movie_type, media_list)
        data = list(map(lambda d: self.data_convent(d, exist_ids), media_list))
        data = list(map(lambda d: self.data_import_check(d, is_movie_type=is_movie_type, series_id=None), data))

        return dict(page_num=int(page),
                    page_size=20,
                    total=result.get('total_results', 0),
                    data=data)

    async def tv_detail_by_series_id(self, series_id, lang='en'):
        r = tmdb.TV(series_id).info(language=lang)
        seasons = r.get('seasons', None)
        if not seasons:
            return r
        ids = list(map(lambda d: d['id'], seasons))
        async with self.session.begin():
            result = await self.session.execute(select(TMDBTVSeason.id).where(TMDBTVSeason.id.in_(ids)))
            exist_ids = result.scalars().all()
            data = list(map(lambda d: self.data_convent(d, set(exist_ids)), seasons))
            data = list(map(lambda d: self.data_import_check(d, is_movie_type=False, series_id=series_id), data))
            return r
