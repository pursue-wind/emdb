import logging

import tmdbsimple as tmdb
from apscheduler.schedulers.tornado import TornadoScheduler
from sqlalchemy import text, select
from sqlalchemy.orm import joinedload

from apps.domain.models import *
from apps.services.people import PeopleService
from apps.services.tv import TVService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class ScheduleService(PeopleService):
    def __init__(self, session):
        super().__init__(session())
        self.tv_service = TVService(session())

    async def start(self):
        scheduler = TornadoScheduler(timezone='Asia/Shanghai')
        # scheduler.add_job(self.sync_tv, 'interval', seconds=30)
        scheduler.add_job(self.sync_tv, 'interval', seconds=3600 * 12)
        scheduler.start()

    async def sync_tv(self):
        language_var.set('en')
        skip_load_var.set(True)
        logging.info("Syncing TV")
        statement = """
                    select tv.id, tv.name, tv.last_episode_to_air, tv.number_of_seasons, count_season_number
                    from tmdb_tv tv
                             left join (select tv_show_id, count(*) count_season_number
                                        from tmdb_tv_seasons
                                        where season_number != 0
                                        group by tv_show_id) ts on tv.id = ts.tv_show_id
                    where tv.status = 'Returning Series'
                    """
        logging.info(f"Executing: {statement}")
        execute_res = await self.session.execute(text(statement))
        res = execute_res.fetchall()
        for it in res:
            tv_id, name, last_episode_to_air, number_of_seasons, count_season_number = it
            season = await self._simple_query(TMDBTVSeason, TMDBTVSeason.tv_show_id == tv_id,
                                              TMDBTVSeason.season_number == number_of_seasons)
            if season and last_episode_to_air and season.episode_count >= last_episode_to_air.get('episode_number', -1):
                continue
            logging.info(f"=> Syncing TV {name}")
            if number_of_seasons == count_season_number:
                r = await self.tv_service.fetch_and_store_tv(tv_id, tv_season_num=number_of_seasons)
                logging.info(r)
            if number_of_seasons > count_season_number:
                r = await self.tv_service.fetch_and_store_tv(tv_id)
                logging.info(r)

        print(res)
