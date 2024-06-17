from apps.handlers.base import BaseHandler
from apps.services.base import AsyncSessionLocal
from apps.services.tv import TVService


class TVHandler(BaseHandler):
    async def post(self, tv_series_id):
        async with AsyncSessionLocal() as session:
            tv_service = TVService(session)
            await tv_service.fetch_and_store_tv(tv_series_id=int(tv_series_id))
        self.success()

    async def get(self, tv_id):
        async with await self.get_session() as session:
            res = await TVService(session).get_tv(int(tv_id))
            self.success(res)



