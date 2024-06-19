# tv_services.py
import asyncio
from datetime import datetime

import requests
import tmdbsimple as tmdb
from objtyping import to_primitive
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

    async def _get_or_create_list(self, model, data_list, defaults_func, key='id', merge=False):
        return [await self._get_or_create(model, data[key], defaults_func(data), merge) for data in data_list]

    async def _get_or_create(self, model, identifier, defaults, merge=False):
        instance = await self.session.get(model, identifier)
        if not instance or merge:
            instance = model(**defaults)
            await self.session.merge(instance)

        return instance

    async def _process_images(self, images, build_func):
        mid = images['id']
        backdrops = images['backdrops']
        logos = images['logos']
        posters = images['posters']
        b = list(map(lambda d: build_func(mid, TMDBImageTypeEnum.backdrop, d), backdrops))
        l = list(map(lambda d: build_func(mid, TMDBImageTypeEnum.logo, d), logos))
        p = list(map(lambda d: build_func(mid, TMDBImageTypeEnum.poster, d), posters))
        all = b + l + p
        self.session.add_all(all)
        await self.session.flush()

    async def _process_videos(self, videos, build_func):
        mid = videos.get('id')
        v = videos.get('results', [])
        b = list(map(lambda d: build_func(mid, d), v))
        self.session.add_all(b)
        await self.session.flush()
