import tmdbsimple as tmdb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.domain.models import *
from apps.services.people import PeopleService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


# tmdb.API_KEY = '71424eb6e25b8d87dc683c59e7feaa88'


class TVService(PeopleService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_tv(self, tv_series_id: int, args: [str]) -> dict:
        query = select(TMDBTV)
        j_seasons = joinedload(TMDBTV.seasons)
        joinedload_options = {
            'created_by': joinedload(TMDBTV.created_by),
            'last_episode_to_air': joinedload(TMDBTV.last_episode_to_air),
            'genres': joinedload(TMDBTV.genres),
            'networks': joinedload(TMDBTV.networks),
            'production_companies': joinedload(TMDBTV.production_companies),
            'production_countries': joinedload(TMDBTV.production_countries),
            'seasons': j_seasons,
            'episodes': j_seasons.joinedload(TMDBTVSeason.episodes),
            'season_cast': j_seasons.joinedload(TMDBTVSeason.tv_season_cast).joinedload(TMDBTVSeasonCast.people),
            'season_crew': j_seasons.joinedload(TMDBTVSeason.tv_season_crew).joinedload(TMDBTVSeasonCrew.people),
            'spoken_languages': joinedload(TMDBTV.spoken_languages),
        }

        # Dynamically add the requested joinedloads to the query
        for arg in args:
            if arg in joinedload_options:
                query = query.options(joinedload_options[arg])

        result = await self.session.execute(query.where(TMDBTV.id == tv_series_id))
        r = result.unique().scalar_one_or_none()

        return self.to_primitive(r)

    async def fetch_and_store_tv(self, tv_series_id: int, tv_season_id: int = None):
        tv = tmdb.TV(tv_series_id)
        lang = self._language()
        details = await self._fetch(lambda: tv.info())
        translations = await self._fetch(lambda: tv.translations())
        images = await self._fetch(lambda: tv.images())
        videos = await self._fetch(lambda: tv.videos())
        # credits = await self._fetch(lambda: tv.credits(language=self._language()))

        async with self.session.begin():
            await self._store_tv(details)
            # 翻译
            await self._process_tv_translations(translations)
            # 图片
            await self._process_images(images, TMDBTVImage)
            # 视频
            await self._process_videos(videos, TMDBTVVideo)
            # 处理每一季和集的信息
            if 'seasons' in details:
                for season_data in details['seasons']:
                    if season_data['id'] == tv_season_id or tv_season_id is None:
                        await self._fetch_and_store_season(details['id'], season_data['season_number'])

    async def _store_tv(self, details, series_credits=None):
        tv = self._build_tv(details)
        await self._associate_entities(tv, details)
        await self.session.merge(tv)
        await self.session.flush()

    def _build_tv(self, details):
        return TMDBTV(
            id=details['id'],
            adult=details['adult'],
            backdrop_path=details.get('backdrop_path'),
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
            popularity=details['popularity'],
            poster_path=details.get('poster_path'),
            status=details.get('status'),
            vote_average=details['vote_average'],
            vote_count=details['vote_count'],
        )

    async def _associate_entities(self, tv, details):
        # 处理相关实体
        tv.genres = await self._get_or_create_list(
            TMDBGenre, details.get('genres', []),
            lambda x: {'id': x['id'], 'name': x['name']},
            merge=True
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
        people_ids = list(map(lambda c: c['id'], casts))
        await self.update_or_create_peoples(people_ids)

        casts_add = list(map(lambda cast_data: {
            "tv_season_id": tv_season.id,
            "people_id": cast_data['id'],
            "character": cast_data.get('character'),
            "order": cast_data.get('order'),
            "credit_id": cast_data.get('credit_id'),
        }, casts))
        await self._batch_insert(TMDBTVSeasonCast, casts_add)

    async def _process_season_crews(self, tv, crews):
        people_ids = list(map(lambda c: c['id'], crews))
        await self.update_or_create_peoples(people_ids)

        crews_add = list(map(lambda crew_data: {
            "tv_season_id": tv.id,
            "people_id": crew_data['id'],
            "department": crew_data.get('department'),
            "job": crew_data.get('job'),
            "credit_id": crew_data.get('credit_id')
        }, crews))
        await self._batch_insert(TMDBTVSeasonCrew, crews_add)

    async def _fetch_and_store_season(self, tv_id: int, season_number: int):
        season = tmdb.TV_Seasons(tv_id, season_number)
        lang = self._language()
        season_details = await self._fetch(lambda: season.info(language=lang))
        season_credits = await self._fetch(lambda: season.credits(language=lang))
        tv_season, tv_season_translation = self._build_tv_season_and_trans(tv_id, season_details)
        await self.session.merge(tv_season)
        await self.session.merge(tv_season_translation)
        await self._process_season_episodes(tv_id, tv_season, season_details.get('episodes', []))
        await self._process_season_credits(tv_season, season_credits)

    def _build_tv_season_and_trans(self, tv_id, season_details):
        return TMDBTVSeason(
            id=season_details['id'],
            tv_show_id=tv_id,
            air_date=season_details.get('air_date'),
            poster_path=season_details['poster_path'],
            season_number=season_details['season_number'],
            vote_average=season_details.get('vote_average', 0)
        ), TMDBTVSeasonTranslation(
            tv_season_id=season_details['id'],
            language=self._language(),
            name=season_details['name'],
            overview=season_details['overview'],
        )

    async def _process_season_episodes(self, tv_id, season, episodes):
        for episode_data in episodes:
            tv_episode = self._build_tv_episode(season.id, episode_data)
            await self.session.merge(tv_episode)
            await self.session.flush()
            lang = self._language()
            episode_credits = await self._fetch(
                lambda: tmdb.TV_Episodes(tv_id, season.season_number, episode_data['episode_number'])
                .credits(language=lang)
            )
            episode_translations = await self._fetch(
                lambda: tmdb.TV_Episodes(tv_id, season.season_number, episode_data['episode_number'])
                .translations()
            )
            await self._process_episode_credits(tv_episode, episode_credits)
            await self._process_episode_translations(episode_translations)

    def _build_tv_episode(self, tv_season_id, episode_data):
        return TMDBTVEpisode(
            id=episode_data['id'],
            tv_season_id=tv_season_id,
            air_date=episode_data.get('air_date'),
            episode_number=episode_data['episode_number'],
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
        people_ids = list(map(lambda c: c['id'], casts))
        await self.update_or_create_peoples(people_ids)

        casts_add = list(map(lambda cast_data: {
            "tv_episodes_id": episode.id,
            "people_id": cast_data.get('id'),
            "character": cast_data.get('character'),
            "order": cast_data.get('order'),
            "credit_id": cast_data.get('credit_id'),
        }, casts))

        await self._batch_insert(TMDBTVEpisodeCast, casts_add)

    async def _process_episode_crews(self, episode, crews):
        people_ids = list(map(lambda c: c['id'], crews))
        await self.update_or_create_peoples(people_ids)
        crews_add = list(map(lambda crew_data: {
            "tv_episode_id": episode.id,
            "people_id": crew_data.get('id'),
            "department": crew_data.get('department'),
            "job": crew_data.get('job'),
            "credit_id": crew_data.get('credit_id')
        }, crews))
        await self._batch_insert(TMDBTVEpisodeCrew, crews_add)

    async def _process_tv_translations(self, translations):
        mid = translations['id']
        t = [
            {
                "tv_id": mid,
                "iso_3166_1": translation['iso_3166_1'],
                "iso_639_1": translation['iso_639_1'],
                "lang_name": translation['name'],
                "english_name": translation['english_name'],
                "homepage": translation['data']['homepage'],
                "overview": translation['data']['overview'],
                "tagline": translation['data']['tagline'],
                "name": translation['data']['name'],
            }
            for translation in translations.get('translations', [])
        ]
        await self._batch_insert(TMDBTVTranslation, t)

    async def _process_episode_translations(self, translations):
        mid = translations['id']
        t = [
            {
                "tv_episode_id": mid,
                "iso_3166_1": translation['iso_3166_1'],
                "iso_639_1": translation['iso_639_1'],
                "lang_name": translation['name'],
                "english_name": translation['english_name'],
                "overview": translation['data']['overview'],
                "name": translation['data']['name'],
            }
            for translation in translations.get('translations', [])
        ]
        await self._batch_insert(TMDBTVEpisodeTranslation, t)
