import asyncio
import copy
import logging
from operator import or_

from objtyping import to_primitive
from sqlalchemy import select, func, distinct, text
from sqlalchemy.orm import joinedload, selectinload, aliased

from apps.domain.base import TMDBImageTypeEnum, movie_upload_progress, tv_upload_progress, tv_upload_progress_build_key
from apps.domain.models import *
from apps.handlers.base import BaseHandler
from apps.services.movie import MovieService
from apps.services.search import SearchService
from apps.services.tv import TVService
from apps.utils.auth_decorators import auth

# 修改路径的函数
p_set = {"backdrop_path", "logo_path", "profile_path", "poster_path", "file_path", "still_path"}


def update_path(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in p_set and isinstance(value, str) and value.startswith("/"):
                data[key] = IMAGE_BASE_URL + value
            elif isinstance(value, (dict, list)):
                update_path(value)
    elif isinstance(data, list):
        for item in data:
            update_path(item)
    return data


def tmdb_img_path_handler(data):
    return update_path(data)


class Movie2Handler(BaseHandler):

    @auth
    async def post(self, *_args, **_kwargs):
        """
        数据入库：必传，电影类型：movie，电视类型：tv
        """
        async with await self.get_session() as session:
            tmdb_id, media_type, tv_season_id, cover = self.parse_body('id', 'media_type',
                                                                       'tv_season_id', 'cover',
                                                                       required=['id', 'media_type'])
            if media_type not in ["movie", "tv"]:
                self.fail(status=400, msg='media_type param err')

            is_movie_type = media_type == 'movie'
            if not is_movie_type and not tv_season_id:
                self.fail(status=400, msg='media_type param err')

            # 强制覆盖的话，不检查是否已存在数据库
            if not cover:
                result = await session.execute(
                    select(TMDBMovie.id).where(TMDBMovie.id == tmdb_id)) if is_movie_type else session.execute(
                    select(TMDBTV.id).where(TMDBTV.id == tmdb_id))
                exist_id = result.scalar_one_or_none()
                if exist_id:
                    self.success(data=list())

            # get_tv_detail_filter_season(tmdb_series_id_list[i], season_id_list[i], company_id)
            if is_movie_type:
                movie_upload_progress.add(tmdb_id)
                asyncio.create_task(MovieService(session).fetch_and_store_movie(tmdb_id)).add_done_callback(
                    lambda t: movie_upload_progress.remove(tmdb_id)
                )
                self.success(data=tmdb_id)
            else:
                tv_upload_progress.add(tv_upload_progress_build_key(tmdb_id, tv_season_id))
                asyncio.create_task(TVService(session).fetch_and_store_tv(tmdb_id, tv_season_id)).add_done_callback(
                    lambda t: tv_upload_progress.remove(tv_upload_progress_build_key(tmdb_id, tv_season_id))
                )
                self.success(data=tmdb_id)


class DiscoverHandler(BaseHandler):
    @auth
    async def get(self, *_args, **_kwargs):
        lang, page, media_type, include_adult = self.parse_form('lang', 'page', 'media_type', 'include_adult')
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')
        async with await self.get_session() as session:
            res = await SearchService(session).discover(lang=lang, page=page, media_type=media_type,
                                                        include_adult=include_adult)
            self.success(data=res)


class TMDBTVDetails(BaseHandler):
    @auth
    async def get(self, *_args, **_kwargs):
        lang, series_id = self.parse_form('lang', 'series_id')
        async with await self.get_session() as session:
            res = await SearchService(session).tv_detail_by_series_id(lang=lang, series_id=series_id)
            self.success_func(data=res, func=tmdb_img_path_handler)


class TMDBSearch(BaseHandler):

    @auth
    async def get(self, *_args, **_kwargs):

        name, lang, page, media_type, include_adult, \
            t_id = self.parse_form('name', 'lang', 'page', 'media_type', 'include_adult', 't_id',
                                   required=['media_type'])
        if media_type not in ["movie", "tv"]:
            self.fail(status=400, msg='media_type param err')
        if name and t_id:
            self.fail(status=400, msg='only name or id')
        async with await self.get_session() as session:
            res = await SearchService(session).search(name, lang=lang, page=page, media_type=media_type, t_id=t_id)
            self.success(data=res)


def transform_image_type(img: TMDBImage, r_id: int):
    _img = to_primitive(img)
    if img.image_type == TMDBImageTypeEnum.backdrop:
        _img['type'] = 3
    elif img.image_type == TMDBImageTypeEnum.logo:
        _img['type'] = 1
    elif img.image_type == TMDBImageTypeEnum.poster:
        _img['type'] = 2
    if not img.iso_639_1:
        _img['iso_639_1'] = 'all'
    _img['id'] = r_id + 1
    return _img


class MovieImagesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieImage).where(TMDBMovieImage.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()
            r_id = int(movie_id + "000")

            r_trans = []
            for img in r:
                r_trans.append(transform_image_type(img, r_id))
                r_id += 1
            res = self.to_primitive(r_trans)
            self.success_func(data={"images": res}, func=tmdb_img_path_handler)


class TVImagesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            tv_id = self.parse_form('tv_id')

            result = await session.execute(select(TMDBTVSeason).where(TMDBTVSeason.id == int(tv_id)))
            r = result.scalars().first()
            if r is None:
                return self.success(data={"images": []})

            query = select(TMDBTVImage).where(TMDBTVImage.tv_id == int(r.tv_show_id))
            result = await session.execute(query)
            r = result.scalars().all()
            r_id = int(tv_id + "000")
            r_trans = []
            for img in r:
                r_trans.append(transform_image_type(img, r_id))
                r_id += 1
            self.success_func(data={"images": r_trans}, func=tmdb_img_path_handler)


class TVEpisodesHandler(BaseHandler):
    @auth
    async def post(self):
        async with await self.get_session() as session:
            tmdb_season_id = self.parse_form('tmdb_season_id')
            query = select(TMDBTVEpisode).where(TMDBTVEpisode.tv_season_id == int(tmdb_season_id)).order_by(
                TMDBTVEpisode.episode_number)
            result = await session.execute(query)
            lis = result.scalars().all()

            def trans(target):
                target_ret = self.to_primitive(target)
                target_ret['tmdb_series_id'] = target_ret['tv_season_id']
                target_ret['tmdb_episode_id'] = target_ret['id']
                target_ret['tmdb_season_id'] = target_ret['tv_season_id']
                # runtime 分转秒 * 60
                all_run_time = target_ret.get('runtime', 0)
                target_ret['runtime'] = all_run_time * 60 if all_run_time else 0
                return target_ret

            tv_res = list(map(lambda x: trans(x), lis))

            self.success_func(data={"episodes_list": tv_res}, func=tmdb_img_path_handler)


class MovieTranslationsHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieTranslation).where(TMDBMovieTranslation.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success(res)


class TVTranslationsHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            tv_id = self.parse_form('tv_id')
            query = select(TMDBTVSeasonTranslation).where(TMDBTVSeasonTranslation.tv_season_id == int(tv_id))
            result = await session.execute(query)
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success(res)


class MovieAlternativeTitlesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieAlternativeTitle).where(TMDBMovieAlternativeTitle.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success({"alternative_titles": res})


class TVAlternativeTitlesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            tv_id = self.parse_form('tv_id')
            query = select(TMDBTVSeason).where(TMDBTVSeason.id == int(tv_id))
            result = await session.execute(query)
            r = result.scalars().first()
            if r is None:
                return self.success(data={"alternative_titles": []})
            query = select(TMDBTVAlternativeTitle).where(TMDBTVAlternativeTitle.tv_id == int(r.tv_show_id))
            result = await session.execute(query)
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success({"alternative_titles": res})


def flatten(target):
    if 'people' in target:
        for p in target['people']:
            target[p] = target['people'][p]
        target['sex'] = target['gender']
    target['people'] = None
    return target


class MovieCreditsHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            async with session.begin():
                movie_id = self.parse_form('movie_id')
                with session.no_autoflush:
                    result = await session.execute(select(TMDBMovieCast).options(joinedload(TMDBMovieCast.people))
                                                   .where(TMDBMovieCast.movie_id == int(movie_id)))
                    cast = result.scalars().all()
                    cast_f = list(map(lambda x: flatten(x), self.to_primitive(cast)))

                    result2 = await session.execute(select(TMDBMovieCrew).options(joinedload(TMDBMovieCrew.people))
                                                    .where(TMDBMovieCrew.movie_id == int(movie_id)))
                    crew = result2.scalars().all()

                    crew_f = list(map(lambda x: flatten(x), self.to_primitive(crew)))
                    res = {"credits": {"cast": cast_f, "crew": crew_f}}

                    self.success_func(data=res, func=tmdb_img_path_handler)


class TVCreditsHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            async with session.begin():
                tv_id = self.parse_form('tv_id')
                result = await session.execute(select(TMDBTVSeasonCast)
                                               .options(joinedload(TMDBTVSeasonCast.people))
                                               .where(TMDBTVSeasonCast.tv_season_id == int(tv_id)))
                cast = result.scalars().all()
                cast_f = list(map(lambda x: flatten(x), self.to_primitive(cast)))

                result2 = await session.execute(select(TMDBTVSeasonCrew)
                                                .options(joinedload(TMDBTVSeasonCrew.people))
                                                .where(TMDBTVSeasonCrew.tv_season_id == int(tv_id)))
                crew = result2.scalars().all()
                crew_f = list(map(lambda x: flatten(x), self.to_primitive(crew)))
                res = {"credits": {"cast": cast_f, "crew": crew_f}}
                self.success_func(data=res, func=tmdb_img_path_handler)


class MovieReleaseDatesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(
                select(TMDBMovieReleaseDate).where(TMDBMovieReleaseDate.movie_id == int(movie_id)))
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success({"release_date": res})


class TVReleaseDatesHandler(BaseHandler):
    @auth
    async def get(self):
        self.success({"release_date": []})


class MovieVideosHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(
                select(TMDBMovieVideo).where(TMDBMovieVideo.movie_id == int(movie_id)))
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success({"videos": res})


class TVVideosHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            tv_id = self.parse_form('tv_id')
            query = select(TMDBTVSeason).where(TMDBTVSeason.id == int(tv_id))
            result = await session.execute(query)
            r = result.scalars().first()
            if r is None:
                return self.success(data={"videos": []})
            result = await session.execute(
                select(TMDBTVVideo).where(TMDBTVVideo.tv_id == int(r.tv_show_id)))
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success({"videos": res})


def trans_production_companies(company):
    company['tmdb_id'] = company['id']
    return company


class SearchCompanyMovies(BaseHandler):
    @auth
    async def post(self):
        async with await self.get_session() as session:
            movie_name, page_num, page_size = self.parse_body('movie_name', 'page_num', 'page_size')
            page_num = int(page_num)
            page_size = int(page_size)
            offset = (page_num - 1) * page_size

            base_query = select(TMDBMovie).distinct().options(
                joinedload(TMDBMovie.genres),
                joinedload(TMDBMovie.alternative_titles),
                joinedload(TMDBMovie.production_countries),
                joinedload(TMDBMovie.spoken_languages),
                joinedload(TMDBMovie.production_companies),
            )
            count_query = select(func.count()).select_from(
                select(TMDBMovie.id).distinct().subquery()
            )
            if movie_name:
                base_query = base_query.outerjoin(TMDBMovie.translations).filter(
                    or_(
                        TMDBMovie.original_title.ilike(f"{movie_name}%"),
                        TMDBMovieTranslation.title.ilike(f"{movie_name}%")
                    )
                )

                # 获取总记录数
                count_query = select(func.count()).select_from(
                    select(TMDBMovie.id).outerjoin(TMDBMovie.translations).filter(
                        or_(
                            TMDBMovie.original_title.ilike(f"{movie_name}%"),
                            TMDBMovieTranslation.title.ilike(f"{movie_name}%")
                        )
                    ).distinct().subquery()
                )

            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # 应用分页
            paginated_query = base_query.offset(offset).limit(page_size)
            result = await session.execute(paginated_query)

            movie_list = result.unique().scalars().all()

            def trans(target):
                target_ret = self.to_primitive(target)
                if 'genres' in target_ret:
                    target_ret['genres'] = list(map(lambda x: x.get('name', ''), target_ret['genres']))
                if 'production_countries' in target_ret:
                    target_ret['production_countries'] = list(map(lambda x: x['iso_3166_1'], target_ret['production_countries']))
                if 'spoken_languages' in target_ret:
                    target_ret['spoken_languages'] = list(map(lambda x: x['iso_639_1'], target_ret['spoken_languages']))
                if 'production_companies' in target_ret:
                    target_ret['production_companies'] = list(
                        map(lambda x: trans_production_companies(x), target_ret['production_companies']))
                if 'keywords' in target_ret:
                    target_ret['keywords'] = list(map(lambda x2: x2['name'], target_ret['keywords']['keywords']))
                target_ret['tmdb_id'] = target_ret['id']
                # runtime 分转秒 * 60
                all_run_time = target_ret.get('runtime', 0)
                target_ret['runtime'] = all_run_time * 60 if all_run_time else 0

                if 'title' in target_ret and target_ret['title'] == "":
                    target_ret['title'] = target_ret['original_title']
                if target_ret['external_ids'] is None:
                    target_ret['external_ids'] = {"id": 101, "imdb_id": target_ret['imdb_id'], "twitter_id": None,
                                                  "facebook_id": None,
                                                  "wikidata_id": None, "instagram_id": None}
                return target_ret

            movie_res = list(map(lambda x: trans(x), movie_list))
            # 返回结果
            res = dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                movies=self.to_primitive(movie_res)
            )
            self.success_func(data=res, func=tmdb_img_path_handler)


class SearchCompanyTV(BaseHandler):
    @auth
    async def post(self):
        async with await self.get_session() as session:
            movie_name, page_num, page_size = self.parse_body('movie_name', 'page_num', 'page_size')
            page_num = int(page_num)
            page_size = int(page_size)
            offset = (page_num - 1) * page_size
            # 构建基础查询
            base_query = (
                select(TMDBTVSeason)
                .distinct()
                .options(joinedload(TMDBTVSeason.tv_show).joinedload(TMDBTV.genres))
                .options(joinedload(TMDBTVSeason.tv_show).joinedload(TMDBTV.alternative_titles))
                .options(joinedload(TMDBTVSeason.tv_show).joinedload(TMDBTV.spoken_languages))
                .options(joinedload(TMDBTVSeason.tv_show).joinedload(TMDBTV.production_countries))
                .options(joinedload(TMDBTVSeason.tv_show).joinedload(TMDBTV.production_companies))
            )

            count_query = select(func.count(distinct(TMDBTVSeason.id)))

            # 如果有movie_name，添加过滤条件
            if movie_name:
                tv_translation_alias = aliased(TMDBTVTranslation)

                tv_query = (
                    select(TMDBTV.id)
                    .distinct()
                    .join(tv_translation_alias, TMDBTV.translations)
                    .filter(
                        or_(
                            TMDBTV.name.ilike(f"{movie_name}%"),
                            tv_translation_alias.name.ilike(f"{movie_name}%")
                        )
                    )
                )

                # 执行查询
                tv_ids_r = await session.execute(tv_query)
                tv_ids = tv_ids_r.scalars().all()
                base_query = base_query.where(TMDBTVSeason.tv_show_id.in_(tv_ids))
                count_query = count_query.where(TMDBTVSeason.tv_show_id.in_(tv_ids))

            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # 应用分页
            paginated_query = base_query.offset(offset).limit(page_size)
            result = await session.execute(paginated_query)

            lis = result.unique().scalars().all()

            tv_season_runtime_dict = {}
            if lis:
                tv_ids = ",".join(set(map(lambda x: str(x.tv_show_id), lis)))
                statement = """
                select show_id, tv_season_id, sum(runtime)
                from tmdb_tv_episodes
                where show_id in ({})
                group by 1, 2
                """.format(tv_ids)
                logging.info(f"Executing: {statement}")
                execute_res = await session.execute(text(statement))
                tv_season_runtime_res = execute_res.fetchall()

                for tv_season_runtime_re in tv_season_runtime_res:
                    _tv_id, _season_id, _runtime = tv_season_runtime_re
                    tv_season_runtime_dict[(_tv_id, _season_id)] = _runtime

            def trans(target):
                tv_season = self.to_primitive(target)
                tv_series = self.to_primitive(target.tv_show)
                tmdb_series_id = tv_series['id']
                tv_season_id = tv_season['id']

                tv_series['source_type'] = 2
                tv_series['original_title'] = tv_series['original_name']
                tv_series['tmdb_series_id'] = tmdb_series_id
                tv_series['id'] = tv_season_id
                tv_series['tmdb_id'] = tv_season_id
                tv_series['tmdb_season_id'] = tv_season_id
                # runtime 分转秒 * 60
                all_run_time = tv_season_runtime_dict.get((tmdb_series_id, tv_season_id), 0)
                tv_series['runtime'] = all_run_time * 60 if all_run_time else 0

                tv_series['external_ids'] = {k: (str(v) if v and k != 'id' else v) for k, v in
                                             tv_series['external_ids'].items()}

                tv_series['title'] = tv_series['name']
                tv_series['revenue'] = 0
                tv_series['budget'] = 0

                if 'overview' in tv_series and tv_series['overview'] == '':
                    tv_series['overview'] = tv_season['overview']
                if 'production_companies' in tv_series:
                    tv_series['production_companies'] = list(
                        map(lambda x: trans_production_companies(x), tv_series['production_companies']))
                if 'genres' in tv_series:
                    tv_series['genres'] = list(map(lambda x: x.name, target.tv_show.genres))

                additional_info = copy.deepcopy(tv_series)

                tv_series['additional_info'] = additional_info

                del tv_season['tv_show']
                tv_season['external_ids'] = tv_series['external_ids']

                tv_season['tmdb_id'] = tv_season_id
                tv_season['tmdb_season_id'] = tv_season_id
                tv_season['tmdb_series_id'] = tmdb_series_id
                tv_series['episode_detail'] = tv_season
                if 'production_countries' in tv_series:
                    tv_series['production_countries'] = list(
                        map(lambda x: x.iso_3166_1, target.tv_show.production_countries))

                if 'spoken_languages' in tv_series:
                    tv_series['spoken_languages'] = list(map(lambda x: x.iso_639_1, target.tv_show.spoken_languages))
                if 'keywords' in tv_series:
                    tv_series['keywords'] = list(map(lambda x2: x2['name'], tv_series['keywords']['results']))

                if 'title' in tv_series and tv_series['title'] == "":
                    tv_series['title'] = tv_series['original_title']

                if tv_series['external_ids'] is None:
                    tv_series['external_ids'] = {"id": 101, "imdb_id": tv_series['imdb_id'], "twitter_id": None,
                                                 "facebook_id": None,
                                                 "wikidata_id": None, "instagram_id": None}
                return tv_series

            tv_res = list(map(lambda x: trans(x), lis))
            # 返回结果
            res = (dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                tvs=self.to_primitive(tv_res)
            ))

            self.success_func(data=res, func=tmdb_img_path_handler)


class CountCompanyMovies(BaseHandler):
    """
    return movie and tv shows number of company
    """

    @auth
    async def get(self, *_args, **_kwargs):
        async with await self.get_session() as session:
            movie_count_result = await session.execute(select(func.count()).select_from(TMDBMovie))
            movie_count = movie_count_result.scalar()

            tv_count_result = await session.execute(select(func.count()).select_from(TMDBTVSeason))
            tv_count = tv_count_result.scalar()

            self.success(data=dict(movie_count=movie_count, tv_count=tv_count))
