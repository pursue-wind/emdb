from sqlalchemy.orm import query

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
            result = await session.execute(query.Query(TMDBMovieImage.movie_id == movie_id))
            r = result.scalars().all()

            return self.to_primitive(r)

class MovieTranslationsHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(query.where(TMDBMovie.id == movie_id))
            r = result.unique().scalar_one_or_none()

            return self.to_primitive(r)

class MovieAlternativeTitlesHandler(BaseHandler):
    async def get(self):
        movie_id = self.get_argument('movie_id')
        http = tornado.httpclient.AsyncHTTPClient()
        response = await http.fetch(f'https://test-xmdb.emmai.com/api/movie/alternative_titles?movie_id={movie_id}')
        self.write(response.body)

class MovieCreditsHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(query.Query(TMDBMovieCast.movie_id == movie_id))
            r = result.scalars().all()
            result2 = await session.execute(query.Query(TMDBMovieCrew.movie_id == movie_id))
            r2 = result2.scalars().all()

            return self.to_primitive(r)
class MovieReleaseDatesHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(query.Query(TMDBMovieReleaseDate.movie_id == movie_id))
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success(res)

class MovieVideosHandler(BaseHandler):
    async def get(self):
        async with await self.get_session() as session:
            movie_id = self.parse_form('movie_id')
            result = await session.execute(query.Query(TMDBMovieVideo.movie_id == movie_id))
            r = result.scalars().all()

            res = self.to_primitive(r)
            self.success(res)