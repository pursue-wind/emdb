# tv_services.py
import asyncio

import requests
import tmdbsimple as tmdb
from objtyping import to_primitive
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import tornado.ioloop

from apps.domain.models import *
from apps.handlers.base import language_var

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'

# 数据库连接配置
DATABASE_URL = 'postgresql+asyncpg://root:1234@127.0.0.1:5432/emdb'
# 创建一个引擎对象，指定数据库连接信息
engine = create_engine('postgresql://root:1234@127.0.0.1:5432/emdb', echo=True)

# 创建一个会话工厂
Session = sessionmaker(bind=engine)
# 异步数据库引擎和会话工厂
async_engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class BaseService:
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
