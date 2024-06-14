from apps.handlers.base import BaseHandler
from apps.services.movie import MovieService


class MovieHandler(BaseHandler):
    async def post(self, movie_id):
        async with await self.get_session() as session:
            await MovieService(session).fetch_and_store_movie(int(movie_id))
        self.success()

    async def get(self, movie_id):
        async with await self.get_session() as session:
            res = await MovieService(session).get_movie(int(movie_id))
            self.success(res)
