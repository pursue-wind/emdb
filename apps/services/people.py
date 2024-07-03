import logging
from typing import List

import tmdbsimple as tmdb
from async_lru import alru_cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.domain.models import *
from apps.services.base import BaseService

# 配置 TMDB API 密钥
tmdb.API_KEY = '71424eb6e25b8d87dc683c59e7feaa88'


class PeopleService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def update_or_create_peoples2(self, people_ids) -> [TMDBPeople]:
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

    @alru_cache(maxsize=2048)
    async def _fetch_person_info(self, people_id: int, lang: str) -> TMDBPeople:
        logging.info(f"=> fetch people info: {people_id}")
        """辅助方法，用于从 TMDB API 获取人物信息，并缓存结果。"""
        people_info = await self._fetch(lambda: tmdb.People(people_id).info(language=lang))
        return TMDBPeople(
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

    async def update_or_create_peoples(self, people_ids: List[int]) -> List[TMDBPeople]:
        lang = self._language()

        # 查询数据库获取存在的 people
        e = await self.session.execute(select(TMDBPeople).where(TMDBPeople.id.in_(people_ids)))
        exist_peoples = e.scalars().all()
        exist_people_ids = {p.id for p in exist_peoples}
        logging.info(f"=> exist_people_ids: {exist_people_ids}")
        # 需要从 API 获取的新 people
        new_people_ids = set(people_ids) - exist_people_ids
        ps_insert = []

        for people_id in new_people_ids:
            people = await self._fetch_person_info(people_id, lang)
            ps_insert.append(people)

        # 更新数据库
        self.session.add_all(ps_insert)

        return exist_peoples + ps_insert
