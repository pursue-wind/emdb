import os
import traceback
from datetime import timedelta

import tmdbsimple as tmdb
from sqlalchemy import select, UniqueConstraint, Numeric, Sequence, text
from apscheduler.schedulers.tornado import TornadoScheduler
from apps.domain.base import Base0
from apps.domain.models import *
from apps.services.movie import MovieService
from apps.services.people import PeopleService
from apps.services.tv import TVService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class ScheduleService(PeopleService):
    def __init__(self, session):
        super().__init__(session())

    async def start(self):
        scheduler = TornadoScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(self.sync_tv, 'interval', seconds=300)
        scheduler.start()

    async def sync_tv(self):
        print("Syncing TV")

        pass
