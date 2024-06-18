from operator import or_

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from apps.domain.base import TMDBImageTypeEnum
from apps.domain.models import *
from apps.handlers.base import BaseHandler
from apps.services.movie import MovieService


class MovieHandler(BaseHandler):
    async def post(self, movie_id):
        async with await self.get_session() as session:
            await MovieService(session).fetch_and_store_movie(int(movie_id))
        self.success()

    async def get(self, movie_id):
        async with await self.get_session() as session:
            args = self.get_arguments('join')
            res = await MovieService(session).get_movie(int(movie_id), args)
            self.success(res)


####################
#  兼容之前的接口
####################

class MovieImagesHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieImage).where(TMDBMovieImage.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()

            def transform_image_type(img: TMDBMovieImage):
                if img.image_type == TMDBImageTypeEnum.backdrop:
                    img.type = 1
                elif img.image_type == TMDBImageTypeEnum.logo:
                    img.type = 2
                elif img.image_type == TMDBImageTypeEnum.poster:
                    img.type = 3
                return img

            r_trans = list(map(lambda x: transform_image_type(x), r))
            res = self.to_primitive(r_trans)
            self.success({"images": res})


class MovieTranslationsHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieTranslation).where(TMDBMovieTranslation.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success(res)


class MovieAlternativeTitlesHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            query = select(TMDBMovieAlternativeTitle).where(TMDBMovieAlternativeTitle.movie_id == int(movie_id))
            result = await session.execute(query)
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success({"alternative_titles": res})


def flatten(target, people):
    attributes = list(map(lambda c: c.name, people.__table__.columns))

    for attr in attributes:
        setattr(target, attr, getattr(people, attr))
    target.people = None
    target.sex = target.gender
    return target


class MovieCreditsHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(select(TMDBMovieCast).options(joinedload(TMDBMovieCast.people)).where(
                TMDBMovieCast.movie_id == int(movie_id)))
            cast = result.scalars().all()
            cast_f = list(map(lambda x: flatten(x, x.people), cast))

            result2 = await session.execute(select(TMDBMovieCrew).options(joinedload(TMDBMovieCrew.people)).where(
                TMDBMovieCrew.movie_id == int(movie_id)))
            crew = result2.scalars().all()
            crew_f = list(map(lambda x: flatten(x, x.people), crew))
            self.success({"cast": self.to_primitive(cast_f), "crew": self.to_primitive(crew_f)})


class MovieReleaseDatesHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(
                select(TMDBMovieReleaseDate).where(TMDBMovieReleaseDate.movie_id == int(movie_id)))
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success({"release_date": res})


class MovieVideosHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(
                select(TMDBMovieVideo).where(TMDBMovieVideo.movie_id == int(movie_id)))
            r = result.scalars().all()
            res = self.to_primitive(r)
            self.success({"videos": res})
            res = self.to_primitive(r)
            self.success({"release_date": res})


class SearchCompanyMovies(BaseHandler):
    async def post(self):
        async with await self.get_session() as session:
            movie_name, page_num, page_size = self.parse_body('movie_name', 'page_num', 'page_size')
            page_num = int(page_num)
            page_size = int(page_size)
            offset = (page_num - 1) * page_size

            base_query = select(TMDBMovie).distinct().options(
                joinedload(TMDBMovie.genres),
                joinedload(TMDBMovie.alternative_titles)
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

            # 返回结果
            self.success(dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                movies=self.to_primitive(movie_list)
            ))


class SearchCompanyTV(BaseHandler):
    async def post(self):
        async with await self.get_session() as session:
            movie_name, page_num, page_size = self.parse_body('movie_name', 'page_num', 'page_size')
            page_num = int(page_num)
            page_size = int(page_size)
            offset = (page_num - 1) * page_size

            # 构建基础查询
            base_query = select(TMDBTV).distinct().options(joinedload(TMDBTV.genres), )
            count_query = select(func.count()).select_from(select(TMDBTV.id).distinct().subquery())
            # 如果有movie_name，添加过滤条件
            if movie_name:
                base_query = base_query.filter(
                    TMDBTV.name.ilike(f"%{movie_name}%"),
                )

                count_query = select(func.count()).select_from(
                    select(TMDBTV.id).filter(
                        TMDBTV.name.ilike(f"%{movie_name}%"),
                    ).distinct().subquery()
                )

            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # 应用分页
            paginated_query = base_query.offset(offset).limit(page_size)
            result = await session.execute(paginated_query)

            lis = result.unique().scalars().all()

            # 返回结果
            self.success(dict(
                page_num=page_num,
                page_size=page_size,
                total=total,
                tvs=self.to_primitive(lis)
            ))
