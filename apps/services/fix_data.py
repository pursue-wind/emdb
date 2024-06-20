import traceback

import tmdbsimple as tmdb
from sqlalchemy import select, UniqueConstraint, Numeric, Sequence

from apps.domain.base import Base0
from apps.domain.models import *
from apps.services.movie import MovieService
from apps.services.people import PeopleService
from apps.services.tv import TVService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'

class Movies(Base0):
    __tablename__ = "movies"
    id = Column(Integer, Sequence("movies_seq"), primary_key=True)
    tmdb_id = Column(Integer, nullable=False, index=True)
    imdb_id = Column(String(10), index=True)
    tmdb_series_id = Column(Integer, nullable=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    backdrop_path = Column(String(200))
    belongs_to_collection = Column(JSONB)
    budget = Column(Integer, default=0)
    genres = Column(ARRAY(Integer))
    homepage = Column(String(200))
    original_language = Column(String(20), nullable=False)
    original_title = Column(String(128), nullable=False)
    overview = Column(Text)
    adult = Column(Boolean, nullable=False)
    popularity = Column(Numeric(10, 3))
    poster_path = Column(String(128))
    production_companies = Column(ARRAY(Integer), doc="制片公司")
    production_countries = Column(ARRAY(String(5)))
    release_date = Column(DateTime)
    revenue = Column(Integer, default=0)
    runtime = Column(Integer, default=0)
    spoken_languages = Column(ARRAY(String(5)))
    status = Column(String(32), nullable=False)
    tagline = Column(Text)
    video = Column(Boolean, default=False)
    vote_average = Column(Numeric(5, 3))
    vote_count = Column(Integer)
    source_type = Column(Integer, default=1)  # 新增字段
    external_ids = Column(JSONB, doc="其他视频平台id")
    __table_args__ = (
        UniqueConstraint('tmdb_id', 'source_type'),
    )


class DataService(PeopleService):
    def __init__(self, session):
        super().__init__(session())
        self.movies_service = MovieService(session())
        self.tv_service = TVService(session())

    async def movie(self):
        batch_size = 100
        offset = 5

        while True:
            # 构建查询
            query = select(Movies.tmdb_id).where(Movies.source_type == 1).offset(offset).limit(batch_size).order_by(
                Movies.tmdb_id)
            result = await self.session.execute(query)
            batch = result.scalars().all()

            if not batch:
                break
            await self.session.commit()
            print(batch)
            for movie_id in batch:
                language_var.set('en')
                try:
                    res = await self.movies_service.fetch_and_store_movie(movie_id)
                except Exception as e:
                    traceback.print_exc()
                    continue
                print(res)
            offset += batch_size
    async def tv(self):
        batch_size = 100
        offset = 0

        while True:
            # 构建查询
            query = (select(Movies.tmdb_id).where(Movies.source_type == 2).offset(offset).limit(batch_size)
            .order_by(Movies.tmdb_id))
            result = await self.session.execute(query)
            batch = result.scalars().all()

            if not batch:
                break
            await self.session.commit()
            print(batch)
            for movie_id in batch:
                language_var.set('en')
                try:
                    res = await self.tv_service.fetch_and_store_tv(movie_id)
                except Exception as e:
                    traceback.print_exc()
                    continue
                print(res)
            offset += batch_size
