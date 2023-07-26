import time

from sqlalchemy import Column, Integer, String, Boolean, Numeric, Text, DateTime, Sequence, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ENUM, ARRAY
from sqlalchemy.orm import relationship

from db.pgsql.base import Base, DB_ENGINE


def init_db():
    # 删除所有表格
    # Base.metadata.drop_all(bind=DB_ENGINE)
    Base.metadata.create_all(bind=DB_ENGINE)


class ProductionCompany(Base):
    __tablename__ = "production_company"
    id = Column(Integer, Sequence("production_company_seq"), primary_key=True)
    name = Column(String(255), index=True)
    tmdb_id = Column(Integer, nullable=False, index=True, unique=True)
    headquarters = Column(String(255), doc="地区")
    homepage = Column(String(255))
    origin_country = Column(String(20))
    parent_company = Column(String(255))
    logo_path = Column(String(120))


class Movies(Base):
    __tablename__ = "movies"
    id = Column(Integer, Sequence("movies_seq"), primary_key=True)
    tmdb_id = Column(Integer, nullable=False, index=True, unique=True)
    imdb_id = Column(String(10), index=True)
    title = Column(String(255), nullable=False, index=True)
    backdrop_path = Column(String(128))
    belongs_to_collection = Column(JSONB)
    budget = Column(Integer)
    genres = Column(ARRAY(Integer))
    homepage = Column(String(128))
    original_language = Column(String(20), nullable=False)
    original_title = Column(String(128), nullable=False)
    overview = Column(Text)
    adult = Column(Boolean, nullable=False)
    popularity = Column(Numeric(5, 3))
    poster_path = Column(String(128))
    production_companies = Column(ARRAY(Integer), doc="制片公司")
    production_countries = Column(ARRAY(String(5)))
    release_date = Column(DateTime)
    revenue = Column(Integer)
    runtime = Column(Integer)
    spoken_languages = Column(ARRAY(String(5)))
    status = Column(String(32), nullable=False)
    tagline = Column(Text)
    video = Column(Boolean)
    vote_average = Column(Numeric(5, 3))
    vote_count = Column(Integer)

    external_ids = Column(JSONB, doc="其他视频平台id")


class MovieKeyWords(Base):
    __tablename__ = 'movie_key_words'
    id = Column(Integer, Sequence('movie_key_words_seq'), primary_key=True)
    tmdb_id = Column(Integer, nullable=False, index=True, unique=True)
    movie_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)


class MovieAlternativeTitles(Base):
    __tablename__ = 'movie_alternative_titles'
    id = Column(Integer, Sequence('movie_alternative_titles_seq'), primary_key=True)
    movie_id = Column(Integer, nullable=False, index=True)
    iso_3166_1 = Column(String(5))
    title = Column(String(100), nullable=False)
    type = Column(String(32))

    __table_args__ = (
        UniqueConstraint('movie_id', 'iso_3166_1', "title"),
    )


class MoviesTranslations(Base):
    __tablename__ = 'movie_translations'
    id = Column(Integer, Sequence('movie_translations_seq'), primary_key=True)
    movie_id = Column(Integer, nullable=False, index=True)
    iso_3166_1 = Column(String(5), index=True)
    iso_639_1 = Column(String(5), index=True)
    name = Column(String(255))
    english_name = Column(String(255))
    homepage = Column(String(255))
    overview = Column(Text)
    runtime = Column(Integer)
    tagline = Column(String(255))
    title = Column(String(255))

    __table_args__ = (
        UniqueConstraint('iso_3166_1', 'iso_639_1'),
    )


class MovieCreditsRelation(Base):

    __tablename__ = 'movie_credits_relation'

    id = Column(Integer, Sequence('movie_credits_relation_seq'), primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)
    credit_id = Column(Integer, ForeignKey('movie_credits.id'), nullable=False, index=True)
    tmdb_credit_id = Column(String(255),nullable=False, unique=True)
    order = Column(Integer)
    character = Column(String(255), default=None)
    department = Column(String(255), default=None)
    job = Column(String(255), default=None)
    type = Column(Integer, index=True, doc="1:演员，2：工作人员")

    movie = relationship("Movies")
    credit = relationship("MoviesCredits")


class MoviesCredits(Base):
    __tablename__ = 'movie_credits'
    id = Column(Integer, Sequence('movie_credits_seq'), primary_key=True)
    tmdb_id = Column(Integer, nullable=False, index=True, unique=True)
    # type = Column(Integer, index=True, doc="1:演员，2：工作人员")
    name = Column(String(255), index=True)
    original_name = Column(String(255))
    popularity = Column(Numeric(6, 3))
    gender = Column(Integer)
    known_for_department = Column(String(255))
    adult = Column(Boolean)
    profile_path = Column(String(255))
    cast_id = Column(Integer, default=None)
    # credit_id = Column(String(255))


class ReleaseDate(Base):
    __tablename__ = 'movie_release_date'
    id = Column(Integer, Sequence('movie_release_date_seq'), primary_key=True)
    movie_id = Column(Integer, nullable=False, index=True)
    iso_3166_1 = Column(String(5), doc="country")
    iso_639_1 = Column(String(5), doc="language")
    certification = Column(String(255))
    descriptors = Column(ARRAY(String(20)))
    note = Column(String(255))
    release_date = Column(DateTime)
    type = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('iso_3166_1', 'release_date'),
    )


class Imgs(Base):
    __tablename__ = 'imgs'
    id = Column(Integer, Sequence('imgs_seq'), primary_key=True)
    movie_id = Column(Integer, nullable=False, index=True)
    iso_639_1 = Column(String(5))
    url = Column(String(128))
    type = Column(Integer, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('movie_id', 'iso_639_1', "url"),
    )


class Videos(Base):
    __tablename__ = 'videos'
    id = Column(Integer, Sequence('videos_seq'), primary_key=True)
    movie_id = Column(Integer, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    type = Column(String(20), doc="视频类型")
    iso_3166_1 = Column(String(5))
    iso_639_1 = Column(String(5))
    url = Column(String(128))
    site = Column(String(32), doc="Vimeo/Youtube")
    key = Column(String(128), nullable=False, doc="第三方视频平台的key")
    size = Column(Integer)
    official = Column(Boolean)
    published_at = Column(DateTime)
    tmdb_id = Column(String(64), unique=True)


class FetchMovieTasks(Base):
    __tablename__ = 'movie_tasks'
    id = Column(Integer, Sequence('movie_tasks_seq'), primary_key=True)
    tmdb_movie_id = Column(Integer, nullable=False, index=True)
    movie_detail = Column(Boolean, nullable=False, default=False)
    credits = Column(Boolean, nullable=False, default=False)
    images = Column(Boolean, nullable=False, default=False)
    videos = Column(Boolean, nullable=False, default=False)
    keywords = Column(Boolean, nullable=False, default=False)
    release_date = Column(Boolean, nullable=False, default=False)
    translations = Column(Boolean, nullable=False, default=False)
    production_companies = Column(Boolean, nullable=False, default=False)

