import logging
from datetime import timedelta

import tmdbsimple as tmdb
from apscheduler.schedulers.tornado import TornadoScheduler
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm

from apps.domain.models import *
from apps.services.people import PeopleService
from apps.services.tv import TVService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class ScheduleService(PeopleService):
    def __init__(self, async_session_factory, interval_sec):
        self.session_factory = async_session_factory
        super().__init__(async_session_factory())
        self.interval_sec = interval_sec

    async def get_session(self) -> AsyncSession:
        return self.session_factory()

    async def start(self):
        scheduler = TornadoScheduler(timezone='Asia/Shanghai')
        scheduler.add_job(self.sync_tv, 'interval', seconds=self.interval_sec)
        scheduler.start()

    async def sync_tv(self):
        language_var.set('en')
        skip_load_var.set(True)
        logging.info("Syncing TV")
        twelve_hours_ago = datetime.utcnow() - timedelta(hours=11)

        result = await self.session.execute(select(TMDBTV).where(
            TMDBTV.status == 'Returning Series',
            # TMDBTV.next_episode_to_air.isnot(None),
            TMDBTV.last_episode_to_air.isnot(None),
            TMDBTV.updated_at < twelve_hours_ago
        ))
        tvs = result.unique().scalars().all()

        for tv in tqdm(tvs, desc="schedule fetch tv:"):
            if not tv.last_episode_to_air:
                print(self.to_primitive(tv))
                continue
            season_number = tv.last_episode_to_air['season_number']
            air_date = tv.last_episode_to_air['air_date']
            episode_number = tv.last_episode_to_air['episode_number']

            season = await self._simple_query_one(
                TMDBTVSeason,
                TMDBTVSeason.tv_show_id == tv.id,
                TMDBTVSeason.season_number == season_number
            )
            # emdb 未导入这一季，跳过
            if not season:
                continue

            if tv.next_episode_to_air is None:
                # 最近更新过，跳过
                air_date_time = datetime.strptime(air_date, '%Y-%m-%d')
                if season.updated_at.date() > air_date_time.date():  # 如果最后一集的播出日期比数据库更新时间更晚
                    continue
                now = datetime.now()
                difference = now - air_date_time

                # 检查两个日期是否相差超过一年
                if difference.days > 365:
                    continue

            if tv.next_episode_to_air and tv.next_episode_to_air != 'null':
                next_season_number = tv.next_episode_to_air['season_number']
                next_air_date = tv.next_episode_to_air['air_date']
                next_episode_number = tv.next_episode_to_air['episode_number']

                next_air_date_time = datetime.strptime(next_air_date, '%Y-%m-%d')

                # 如果下一集的播出日期没超过当前时间，需要更新
                if next_air_date_time.date() <= datetime.now().date():
                    logging.info("schedule fetch_and_store_tv: tv id: {}, tv_season: {}, episode: {}".format(tv.id,
                                                                                                             season_number,
                                                                                                             episode_number))
                    if next_episode_number - episode_number == 1:
                        async with await self.get_session() as session:
                            r = await TVService(session).fetch_and_store_tv(tv.id,
                                                                            tv_season_num=season_number,
                                                                            tv_episode_num=next_episode_number)
                    else:
                        async with await self.get_session() as session:
                            r = await TVService(session).fetch_and_store_tv(tv.id,
                                                                            tv_season_num=season_number)
                # 如果下一集是下一季，更新下一季
                if next_season_number > season_number:
                    async with await self.get_session() as session:
                        r = await TVService(session).fetch_and_store_tv(tv.id, tv_season_num=next_season_number)

            logging.info(f"=> Syncing TV: {tv.id}, {season_number}")


