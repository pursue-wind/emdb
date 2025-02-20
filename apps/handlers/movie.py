from apps.handlers.base import BaseHandler
from apps.services.movie import MovieService
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
            if not res:
                return self.fail(1, "need import")
            self.success(res)
