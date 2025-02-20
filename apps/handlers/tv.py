from apps.handlers.base import BaseHandler
from apps.services.tv import TVService
from apps.utils.auth_decorators import auth


class TVHandler(BaseHandler):
    @auth
    async def post(self, tv_series_id):
        async with await self.get_session() as session:
            tv_service = TVService(session)
            await tv_service.fetch_and_store_tv(tv_series_id=int(tv_series_id))
        self.success()


    @auth
    async def get(self, tv_id):
        async with await self.get_session() as session:
            args = self.get_arguments('join')
            res = await TVService(session).get_tv(int(tv_id), args)
            self.success(res)
