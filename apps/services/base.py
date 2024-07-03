# tv_services.py
import asyncio
import logging
import traceback
from datetime import datetime

import requests
import tmdbsimple as tmdb
from objtyping import to_primitive
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import tornado.ioloop

from apps.domain.base import TMDBImageTypeEnum
from apps.domain.models import *
from apps.handlers.base import language_var

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class BaseService:
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def to_primitive(sqlalchemy_obj):
        return to_primitive(sqlalchemy_obj)

    @staticmethod
    def _language():
        return language_var.get()

    @staticmethod
    def _str_limit2(data):
        if len(data) > 2:
            logging.warning(f"!!! iso_639_1 or iso_3611 is too long: {data}")
        return str(data).strip()[:2]

    async def _fetch_all(self, funcs):
        """并行获取所有函数的结果"""
        return await asyncio.gather(*[self._fetch(func) for func in funcs])

    async def _fetch(self, func):
        """调用tmdb接口报错时会自动等待重试"""
        try:
            return await tornado.ioloop.IOLoop.current().run_in_executor(None, func)
        except requests.exceptions.SSLError as e:
            print(f"SSLError occurred: {e}")
            if "HTTPSConnectionPool(host='api.themoviedb.org', port=443): Max retries exceeded with url" in str(e):
                await asyncio.sleep(3)  # Sleep for 3 seconds before retrying
                return await self._fetch(func)  # Retry the function
            raise e

    async def _get_or_create_list(self, model, data_list, defaults_func, key='id', data_insert=True):
        rs = [defaults_func(data) for data in data_list]
        if data_insert:
            await self._batch_insert(model, rs)
        return [model(**data) for data in rs]

    async def _process_images(self, images, obj):
        mid = images['id']
        backdrops = images['backdrops']
        logos = images['logos']
        posters = images['posters']
        b = list(map(lambda d: obj.build(mid, TMDBImageTypeEnum.backdrop, d), backdrops))
        l = list(map(lambda d: obj.build(mid, TMDBImageTypeEnum.logo, d), logos))
        p = list(map(lambda d: obj.build(mid, TMDBImageTypeEnum.poster, d), posters))
        all = b + l + p
        await self._batch_insert(obj, all)

    async def _process_videos(self, videos, obj):
        mid = videos.get('id')
        v = videos.get('results', [])
        b = list(map(lambda d: obj.build(mid, d), v))
        await self._batch_insert(obj, b)

    async def _batch_insert(self, obj, dict_list):
        if not dict_list:
            logging.warning("not found data: " + str(obj))
            return
        stmt = insert(obj).values(dict_list)
        stmt = stmt.on_conflict_do_nothing()
        try:
            await self.session.execute(stmt)
        except Exception as e:
            traceback.print_exc()
            logging.error(e)

    async def _simple_query_one(self, obj, *whereclause, joinedload_options: [] = []):
        query = select(obj)

        for arg in joinedload_options:
            query = query.options(joinedload_options[arg])

        result = await self.session.execute(query.where(*whereclause))
        r = result.unique().scalar_one_or_none()

        return r

    async def _simple_query_list(self, obj, *whereclause, joinedload_options: [] = []):
        query = select(obj)

        for arg in joinedload_options:
            query = query.options(joinedload_options[arg])

        result = await self.session.execute(query.where(*whereclause))
        r = result.unique().scalars().all()

        return r
