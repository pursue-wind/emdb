import logging
import random
from operator import or_

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from apps.domain.base import TMDBImageTypeEnum
from apps.domain.models import *
from apps.handlers.base import BaseHandler
from apps.services.movie import MovieService
from apps.services.search import SearchService
from apps.services.tv import TVService
from apps.utils.auth_decorators import auth


class MovieHandler(BaseHandler):
    @auth
    async def post(self, movie_id):
        async with await self.get_session() as session:
            await MovieService(session).fetch_and_store_movie(int(movie_id))
        self.success()

    @auth
    async def get(self, movie_id):
        async with await self.get_session() as session:
            args = self.get_arguments('join')
            res = await MovieService(session).get_movie(int(movie_id), args)
            self.success(res)


####################
#  兼容之前的接口
####################

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
                result = await  session.execute(
                    select(TMDBMovie.id).where(TMDBMovie.id == tmdb_id)) if is_movie_type else session.execute(
                    select(TMDBTV.id).where(TMDBTV.id == tmdb_id))
                exist_id = result.scalar_one_or_none()
                if exist_id:
                    self.success(data=list())

            # get_tv_detail_filter_season(tmdb_series_id_list[i], season_id_list[i], company_id)
            if is_movie_type:
                r = await MovieService(session).get_movie(tmdb_id)
                self.success(data=tmdb_id)
            else:
                r = await TVService(session).fetch_and_store_tv(tmdb_id, tv_season_id)
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
            self.success(data=res)


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


class MovieImagesHandler(BaseHandler):
    @auth
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieImage).where(TMDBMovieImage.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()

            def transform_image_type(img: TMDBMovieImage):
                if img.image_type == TMDBImageTypeEnum.backdrop:
                    img.type = 3
                elif img.image_type == TMDBImageTypeEnum.logo:
                    img.type = 1
                elif img.image_type == TMDBImageTypeEnum.poster:
                    img.type = 2
                if not img.iso_639_1:
                    img.iso_639_1 = 'all'

                return img

            r_trans = list(map(lambda x: transform_image_type(x), r))
            res = self.to_primitive(r_trans)
            self.success({"images": res})


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


def flatten(target, people):
    if people:
        attributes = list(map(lambda c: c.name, people.__table__.columns))

        for attr in attributes:
            if attr != "id":
                setattr(target, attr, getattr(people, attr))
        target.sex = target.gender
    else:
        logging.warning('No people found')
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
                    cast_f = list(map(lambda x: flatten(x, x.people), cast))

                    result2 = await session.execute(select(TMDBMovieCrew).options(joinedload(TMDBMovieCrew.people))
                                                    .where(TMDBMovieCrew.movie_id == int(movie_id)))
                    crew = result2.scalars().all()
                    crew_f = list(map(lambda x: flatten(x, x.people), crew))
                    res = {"credits": {"cast": self.to_primitive(cast_f), "crew": self.to_primitive(crew_f)}}
                    self.success(res)


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
                select(TMDBMovie.id).outerjoin(TMDBMovie.alternative_titles).distinct().subquery()
            )
            if movie_name:
                base_query = base_query.outerjoin(TMDBMovie.alternative_titles).filter(
                    or_(
                        TMDBMovie.original_title.ilike(f"%{movie_name}%"),
                        TMDBMovieAlternativeTitle.title.ilike(f"%{movie_name}%")
                    )
                )

                # 获取总记录数
                count_query = select(func.count()).select_from(
                    select(TMDBMovie.id).outerjoin(TMDBMovie.alternative_titles).filter(
                        or_(
                            TMDBMovie.original_title.ilike(f"%{movie_name}%"),
                            TMDBMovieAlternativeTitle.title.ilike(f"%{movie_name}%")
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
                    target_ret['genres'] = list(map(lambda x: x.name, target.genres))
                if 'production_countries' in target_ret:
                    target_ret['production_countries'] = list(map(lambda x: x.iso_3166_1, target.production_countries))
                if 'spoken_languages' in target_ret:
                    target_ret['spoken_languages'] = list(map(lambda x: x.iso_639_1, target.spoken_languages))
                if 'keywords' in target_ret:
                    target_ret['keywords'] = list(map(lambda x2: x2['name'], target_ret['keywords']['keywords']))
                target_ret['tmdb_id'] = target_ret['id']
                if target_ret['backdrop_path']:
                    target_ret['backdrop_path'] = IMAGE_BASE_URL + target_ret['backdrop_path']
                if target_ret['poster_path']:
                    target_ret['poster_path'] = IMAGE_BASE_URL + target_ret['poster_path']
                if 'title' in target_ret and target_ret['title'] == "":
                    target_ret['title'] = target_ret['original_title']
                if target_ret['external_ids'] is None:
                    target_ret['external_ids'] = {"id": 101, "imdb_id": target_ret['imdb_id'], "twitter_id": None,
                                                  "facebook_id": None,
                                                  "wikidata_id": None, "instagram_id": None}
                return target_ret

            movie_res = list(map(lambda x: trans(x), movie_list))
            # 返回结果
            self.success(dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                movies=self.to_primitive(movie_res)
            ))


class SearchCompanyTV(BaseHandler):
    @auth
    async def post(self):
        async with await self.get_session() as session:
            movie_name, page_num, page_size = self.parse_body('movie_name', 'page_num', 'page_size')
            page_num = int(page_num)
            page_size = int(page_size)
            offset = (page_num - 1) * page_size

            # 构建基础查询
            base_query = select(TMDBTV).distinct().options(
                joinedload(TMDBTV.genres),
                joinedload(TMDBTV.alternative_titles),
                joinedload(TMDBTV.production_countries),
                joinedload(TMDBTV.spoken_languages),
                joinedload(TMDBTV.production_companies),
            )
            count_query = select(func.count()).select_from(
                select(TMDBTV.id).outerjoin(TMDBMovie.alternative_titles).distinct().subquery())
            # 如果有movie_name，添加过滤条件
            if movie_name:
                base_query = base_query.filter(
                    or_(
                        TMDBTV.name.ilike(f"%{movie_name}%"),
                        TMDBTVAlternativeTitle.title.ilike(f"%{movie_name}%")
                    )
                )

                count_query = select(func.count()).select_from(
                    select(TMDBTV.id).outerjoin(TMDBTV.alternative_titles).filter(
                        or_(
                            TMDBTV.name.ilike(f"%{movie_name}%"),
                            TMDBTVAlternativeTitle.title.ilike(f"%{movie_name}%")
                        )
                    ).distinct().subquery()
                )

            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # 应用分页
            paginated_query = base_query.offset(offset).limit(page_size)
            result = await session.execute(paginated_query)

            lis = result.unique().scalars().all()

            def trans(target):
                target_ret = self.to_primitive(target)
                if 'genres' in target_ret:
                    target_ret['genres'] = list(map(lambda x: x.name, target.genres))
                if 'production_countries' in target_ret:
                    target_ret['production_countries'] = list(map(lambda x: x.iso_3166_1, target.production_countries))
                if 'spoken_languages' in target_ret:
                    target_ret['spoken_languages'] = list(map(lambda x: x.iso_639_1, target.spoken_languages))
                if 'keywords' in target_ret:
                    target_ret['keywords'] = list(map(lambda x2: x2['name'], target_ret['keywords']['results']))
                target_ret['tmdb_id'] = target_ret['id']
                if target_ret['backdrop_path']:
                    target_ret['backdrop_path'] = IMAGE_BASE_URL + target_ret['backdrop_path']
                if target_ret['poster_path']:
                    target_ret['poster_path'] = IMAGE_BASE_URL + target_ret['poster_path']
                if 'name' in target_ret:
                    target_ret['title'] = target_ret['name']
                if 'title' in target_ret and target_ret['title'] == "":
                    target_ret['title'] = target_ret['original_title']

                if target_ret['external_ids'] is None:
                    target_ret['external_ids'] = {"id": 101, "imdb_id": target_ret['imdb_id'], "twitter_id": None,
                                                  "facebook_id": None,
                                                  "wikidata_id": None, "instagram_id": None}
                return target_ret

            tv_res = list(map(lambda x: trans(x), lis))
            # 返回结果
            self.success(dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                tvs=self.to_primitive(tv_res)
            ))
