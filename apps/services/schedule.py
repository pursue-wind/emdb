import logging
from datetime import timedelta

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
        scheduler.add_job(self.sync_tv, 'interval', seconds=10)
        # scheduler.add_job(self.sync_tv, 'interval', seconds=3600 * 12)
        scheduler.start()

    async def sync_tv(self):
        language_var.set('en')
        skip_load_var.set(True)
        logging.info("Syncing TV")
        twelve_hours_ago = datetime.utcnow() - timedelta(hours=11)

        tvs = await self._simple_query_list(
            TMDBTV,
            TMDBTV.status == 'Returning Series',
            # TMDBTV.next_episode_to_air.isnot(None),
            TMDBTV.last_episode_to_air.isnot(None),
            TMDBTV.updated_at < twelve_hours_ago  # updated_at 是11小时前的
        )

        for tv in tvs:
            if not tv.last_episode_to_air:
                print(self.to_primitive(tv))
                continue
            season_number = tv.last_episode_to_air['season_number']
            air_date = tv.last_episode_to_air['air_date']
            episode_number = tv.last_episode_to_air['episode_number']

            if tv.id == 76479:
                print(tv)

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
                if season.updated_at.date() > air_date_time.date(): # 如果最后一集的播出日期比数据库更新时间更晚
                    continue
                now = datetime.now()
                difference = now - air_date_time

                # 检查两个日期是否相差超过一年
                if difference.days > 365:
                    continue

            if tv.next_episode_to_air:
                next_season_number = tv.next_episode_to_air['season_number']
                next_air_date = tv.next_episode_to_air['air_date']
                next_episode_number = tv.next_episode_to_air['episode_number']

                next_air_date_time = datetime.strptime(next_air_date, '%Y-%m-%d')

                # 如果下一集的播出日期没超过当前时间，需要更新
                if next_air_date_time.date() <= datetime.now().date():
                    r = await self.tv_service.fetch_and_store_tv(tv.id, tv_season_num=season_number)

                # 如果下一集是下一季，更新下一季
                if next_season_number > season_number:
                    await self.tv_service.fetch_and_store_tv(tv.id, tv_season_num=next_season_number)

            logging.info(f"=> Syncing TV: {tv.id}, {season_number}")


    async def sync_tv2(self):
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
            season = await self._simple_query_one(TMDBTVSeason, TMDBTVSeason.tv_show_id == tv_id,
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
