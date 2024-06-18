import tmdbsimple as tmdb
from sqlalchemy.ext.asyncio import AsyncSession

from apps.domain.models import *
from apps.services.base import BaseService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class PeopleService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

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
