import os
import traceback

import tmdbsimple as tmdb
from sqlalchemy import select, UniqueConstraint, Numeric, Sequence, text

from apps.domain.base import Base0
from apps.domain.models import *
from apps.services.movie import MovieService
from apps.services.people import PeopleService
from apps.services.tv import TVService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class Movies(Base0):
    """
    支持原数据库表的查询
    """
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

    async def read_all_genre_by_sql_file(self):
        # 获取当前文件的路径
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        print("current_dir:", current_dir)
        await self.exec_sql_file(current_dir+'/../../sql/tmdb_genres.sql')
        await self.exec_sql_file(current_dir+'/../../sql/tmdb_genres_translations.sql')

    async def exec_sql_file(self, sql_file_path):
        # 检查 SQL 文件是否存在
        if not os.path.isfile(sql_file_path):
            raise FileNotFoundError(f"The SQL file at {sql_file_path} was not found.")

        # 读取 SQL 文件的内容
        with open(sql_file_path, 'r') as file:
            sql_commands = file.read()

        # 创建会话
        async with self.session.begin():
            # 执行每个 SQL 语句
            for statement in sql_commands.split(';'):
                statement = statement.strip()
                if statement:
                    print(f"Executing: {statement}")
                    await self.session.execute(text(statement))

        print("SQL file has been executed successfully.")

    async def get_all_genre_from_tmdb(self):
        """
        多语言的分类数据，启动的时候根据配置 genres_sync: true 拉取所有的分类数据
        """
        lis = [
            'zh', 'en', 'hu', 'it', 'de', 'pt', 'es', 'fr', 'bg', 'he', 'ko', 'da', 'el', 'ru',
            'ro', 'tr', 'nl', 'pl', 'sv', 'cs', 'id', 'uk', 'sg', 'lb', 'ja', 'sr', 'fi', 'fa', 'no',
            'lv', 'lt', 'sk', 'ka', 'ar', 'be', 'uz', 'sl', 'th', 'et', 'vi', 'ca', 'my'
        ]
        g = tmdb.genres.Genres()
        for lang in lis:
            res = await self._fetch(lambda: g.movie_list(language=lang))
            res2 = await self._fetch(lambda: g.tv_list(language=lang))
            all_lis = res.get('genres', []) + res2.get('genres', [])

            ls = list(map(lambda translation: {
                "genre_id": translation['id'],
                "language": lang,
                "name": translation['name'],
            }, filter(lambda translation: translation['name'], all_lis)))
            all_ids = list(map(lambda x: {'id': x['genre_id']}, ls))
            async with self.session.begin():
                if all_ids:
                    await self._batch_insert(TMDBGenre, all_ids)
                if ls:
                    await self._batch_insert(TMDBGenreTranslation, ls)

    async def movie(self, force=False):
        batch_size = 100
        offset = 0

        while True:
            # 构建查询
            query = select(Movies.tmdb_id).where(Movies.source_type == 1).offset(offset).limit(batch_size).order_by(
                Movies.tmdb_id)
            result = await self.session.execute(query)
            batch = result.scalars().all()

            if not batch:
                break
            await self.session.commit()
            need_fetch = set(batch)
            if not force:
                result = await self.session.execute(select(TMDBMovie.id).where(TMDBMovie.id.in_(batch)))
                exist_ids = result.scalars().all()
                need_fetch = set(batch) - set(exist_ids)

            if need_fetch:
                print(need_fetch)
            for movie_id in need_fetch:
                language_var.set('en')
                try:
                    res = await self.movies_service.fetch_and_store_movie(movie_id)
                except Exception as e:
                    traceback.print_exc()
                    continue
                print(res)
            offset += batch_size

    async def tv(self, force=False):
        batch_size = 100
        offset = 0

        while True:
            # 构建查询
            query = (select(Movies.tmdb_series_id).where(Movies.source_type == 2).offset(offset).limit(batch_size)
                     .order_by(Movies.tmdb_id))
            result = await self.session.execute(query)
            batch = result.scalars().all()

            if not batch:
                break
            await self.session.commit()
            print(batch)
            need_fetch = set(batch)
            if not force:
                result = await self.session.execute(select(TMDBTV.id).where(TMDBTV.id.in_(batch)))
                exist_ids = result.scalars().all()
                need_fetch = set(batch) - set(exist_ids)

            for movie_id in need_fetch:
                language_var.set('en')
                try:
                    res = await self.tv_service.fetch_and_store_tv(movie_id)
                except Exception as e:
                    traceback.print_exc()
                    continue
                print(res)
            offset += batch_size
