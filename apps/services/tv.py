# tv_services.py

import tmdbsimple as tmdb
import tornado.ioloop
from sqlalchemy.ext.asyncio import AsyncSession

from apps.handlers.base import language_var
from apps.services.base import AsyncSessionLocal
from apps.services.people import PeopleService
from apps.domain.models import *

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class TVService(PeopleService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def fetch_and_store_tv(self, tv_series_id: int):
        tv = tmdb.TV(tv_series_id)
        details = await self._fetch(lambda: tv.info(language=self._language()))
        # credits = await self._fetch(lambda: tv.credits(language=self._language()))
        await self._store_tv(details)

        # 处理每一季和集的信息
        if 'seasons' in details:
            for season_data in details['seasons']:
                await self._fetch_and_store_season(details['id'], season_data['season_number'])

    async def _store_tv(self, details, series_credits=None):
        async with self.session.begin():
            tv = self._build_tv(details)
            await self._associate_entities(tv, details)
            await self.session.merge(tv)
            await self.session.flush()

    def _build_tv(self, details):
        return TMDBTV(
            id=details['id'],
            adult=details['adult'],
            backdrop_path=details.get('backdrop_path'),
            homepage=details.get('homepage'),
            episode_run_time=details.get('episode_run_time'),
            first_air_date=details.get('first_air_date'),
            in_production=details.get('in_production'),
            languages=details.get('languages'),
            last_air_date=details.get('last_air_date'),
            name=details.get('name'),
            next_episode_to_air=details.get('next_episode_to_air'),
            number_of_episodes=details.get('number_of_episodes'),
            number_of_seasons=details.get('number_of_seasons'),
            original_language=details['original_language'],
            original_name=details['original_name'],
            origin_country=details['origin_country'],
            overview=details.get('overview'),
            popularity=details['popularity'],
            poster_path=details.get('poster_path'),
            status=details.get('status'),
            tagline=details.get('tagline'),
            title=details.get('title'),
            vote_average=details['vote_average'],
            vote_count=details['vote_count'],
        )

    async def _associate_entities(self, tv, details):
        # 处理相关实体
        tv.genres = await self._get_or_create_list(
            TMDBGenre, details.get('genres', []),
            lambda x: {'name': x['name']}
        )

        tv.production_companies = await self._get_or_create_list(
            TMDBProductionCompany,
            details.get('production_companies', []),
            lambda x: {
                'id': x.get('id'),
                'logo_path': x.get('logo_path'),
                'name': x['name'],
                'origin_country': x['origin_country']
            }
        )

        tv.production_countries = await self._get_or_create_list(
            TMDBProductionCountry,
            details.get('production_countries', []),
            lambda x: {
                'iso_3166_1': x['iso_3166_1'],
                'name': x['name']
            }, key='iso_3166_1'
        )

        tv.spoken_languages = await self._get_or_create_list(
            TMDBSpokenLanguage, details.get('spoken_languages', []),
            lambda x: {
                'iso_639_1': x['iso_639_1'],
                'english_name': x.get('english_name'),
                'name': x['name']
            }, key='iso_639_1'
        )

    async def _process_season_credits(self, tv_season, credits):
        await self._process_season_casts(tv_season, credits['cast'])
        await self._process_season_crews(tv_season, credits['crew'])

    async def _process_season_casts(self, tv_season, casts):
        for cast_data in casts:
            people = await self.update_or_create_people(cast_data['id'])
            cast = TMDBTVSeasonCast(
                tv_season_id=tv_season.id,
                people_id=people.id,
                character=cast_data.get('character'),
                order=cast_data.get('order'),
                credit_id=cast_data.get('credit_id'),
                cast_id=cast_data.get('cast_id')
            )
            self.session.add(cast)

    async def _process_season_crews(self, tv, crews):
        for crew_data in crews:
            people = await self.update_or_create_people(crew_data['id'])
            crew = TMDBTVSeasonCrew(
                tv_season_id=tv.id,
                people_id=people.id,
                department=crew_data.get('department'),
                job=crew_data.get('job'),
                credit_id=crew_data.get('credit_id')
            )
            self.session.add(crew)

    async def _fetch_and_store_season(self, tv_id: int, season_number: int):
        season = tmdb.TV_Seasons(tv_id, season_number)
        season_details = await self._fetch(lambda: season.info(language=self._language()))
        season_credits = await self._fetch(lambda: season.credits(language=self._language()))
        async with self.session.begin():
            tv_season = self._build_tv_season(tv_id, season_details)
            await self.session.merge(tv_season)
            await self.session.flush()
            await self._process_season_episodes(tv_id, tv_season, season_details.get('episodes', []))
            await self._process_season_credits(tv_season, season_credits)

    def _build_tv_season(self, tv_id, season_details):
        return TMDBTVSeason(
            id=season_details['id'],
            tv_show_id=tv_id,
            air_date=season_details.get('air_date'),
            name=season_details['name'],
            overview=season_details['overview'],
            poster_path=season_details['poster_path'],
            season_number=season_details['season_number'],
            vote_average=season_details.get('vote_average', 0)
        )

    async def _process_season_episodes(self, tv_id, season, episodes):
        for episode_data in episodes:
            tv_episode = self._build_tv_episode(season.id, episode_data)
            await self.session.merge(tv_episode)
            await self.session.flush()
            episode_credits = await self._fetch(
                lambda: tmdb.TV_Episodes(tv_id, season.season_number, episode_data['episode_number'])
                .credits(language=self._language())
            )
            await self._process_episode_credits(tv_episode, episode_credits)

    def _build_tv_episode(self, tv_season_id, episode_data):
        return TMDBTVEpisode(
            id=episode_data['id'],
            tv_season_id=tv_season_id,
            air_date=episode_data.get('air_date'),
            episode_number=episode_data['episode_number'],
            name=episode_data['name'],
            overview=episode_data['overview'],
            production_code=episode_data.get('production_code'),
            runtime=episode_data.get('runtime'),
            season_number=episode_data['season_number'],
            vote_average=episode_data['vote_average'],
            vote_count=episode_data['vote_count']
        )

    async def _process_episode_credits(self, episode, credits):
        await self._process_episode_casts(episode, credits.get('cast', []))
        await self._process_episode_crews(episode, credits.get('crew', []))

    async def _process_episode_casts(self, episode, casts):
        for cast_data in casts:
            people = await self.update_or_create_people(cast_data['id'])
            cast = TMDBTVEpisodeCast(
                tv_episodes_id=episode.id,
                people_id=people.id,
                character=cast_data.get('character'),
                order=cast_data.get('order'),
                credit_id=cast_data.get('credit_id'),
                cast_id=cast_data.get('cast_id')
            )
            self.session.add(cast)

    async def _process_episode_crews(self, episode, crews):
        for crew_data in crews:
            people = await self.update_or_create_people(crew_data['id'])
            crew = TMDBTVEpisodeCrew(
                tv_episode_id=episode.id,
                people_id=people.id,
                department=crew_data.get('department'),
                job=crew_data.get('job'),
                credit_id=crew_data.get('credit_id')
            )
            self.session.add(crew)


async def main():
    # 创建一个数据库会话实例
    async with AsyncSessionLocal() as session:
        tv_service = TVService(session)
        await tv_service.fetch_and_store_tv(tv_series_id=500)  # 用 TV 的 ID 调用服务


if __name__ == '__main__':
    tornado.ioloop.IOLoop.current().run_sync(main)
