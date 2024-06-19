import tmdbsimple as tmdb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.domain.models import *
from apps.services.base import BaseService
from apps.utils.auth_decorators import async_lru_cache

# 配置 TMDB API 密钥
tmdb.API_KEY = '71424eb6e25b8d87dc683c59e7feaa88'


class PeopleService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    @async_lru_cache(maxsize=128)
    async def update_or_create_people(self, people_id):
        people = await self.session.get(TMDBPeople, people_id)
        if not people:
            lang = self._language()
            people_info = await self._fetch(lambda: tmdb.People(people_id).info(language=lang))
            people = TMDBPeople(
                id=people_info['id'],
                adult=people_info['adult'],
                biography=people_info.get('biography'),
                birthday=people_info.get('birthday'),
                deathday=people_info.get('deathday'),
                gender=people_info['gender'],
                homepage=people_info.get('homepage'),
                imdb_id=people_info.get('imdb_id'),
                known_for_department=people_info.get('known_for_department'),
                name=people_info['name'],
                place_of_birth=people_info.get('place_of_birth'),
                popularity=people_info['popularity'],
                profile_path=people_info.get('profile_path'),
                also_known_as=people_info.get('also_known_as')
            )
            self.session.add(people)
            return people

        return people

    async def update_or_create_peoples(self, people_ids) -> [TMDBPeople]:
        lang = self._language()
        e = await self.session.execute(select(TMDBPeople).where(TMDBPeople.id.in_(people_ids)))
        exist_peoples = e.scalars().all()
        exist_people_ids = list(map(lambda c: c.id, exist_peoples))

        ps = set(people_ids) - set(exist_people_ids)
        ps_insert = []
        for people_id in ps:
            people_info = await self._fetch(lambda: tmdb.People(people_id).info(language=lang))
            people = TMDBPeople(
                id=people_info['id'],
                adult=people_info['adult'],
                biography=people_info.get('biography'),
                birthday=people_info.get('birthday'),
                deathday=people_info.get('deathday'),
                gender=people_info['gender'],
                homepage=people_info.get('homepage'),
                imdb_id=people_info.get('imdb_id'),
                known_for_department=people_info.get('known_for_department'),
                name=people_info['name'],
                place_of_birth=people_info.get('place_of_birth'),
                popularity=people_info['popularity'],
                profile_path=people_info.get('profile_path'),
                also_known_as=people_info.get('also_known_as')
            )
            ps_insert.append(people)

        self.session.add_all(ps_insert)

        return exist_peoples + ps_insert
