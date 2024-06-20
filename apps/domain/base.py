import enum

from sqlalchemy import ForeignKey, ARRAY, Column, Integer, String, Boolean, Float, TIMESTAMP, text, Enum, event
from sqlalchemy.orm import object_session, declarative_base, relationship

from apps.handlers.base import language_var

Base0 = declarative_base()
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"


class Base(Base0):
    __abstract__ = True
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), nullable=False,
                        onupdate=text('CURRENT_TIMESTAMP'))


# 通用的翻译表事件加载方法
def load_translation(target, context, translation_model, foreign_key_field, attributes):
    language = language_var.get()
    if language:
        session = object_session(target)
        if session:
            filters = {foreign_key_field: target.id, 'language': language}
            translation = session.query(translation_model).filter_by(**filters).first()

            if translation:
                for attr in attributes:
                    setattr(target, attr, getattr(translation, attr))


def load_translation_by_iso_639_1(target, context, translation_model, foreign_key_field, attributes):
    language = language_var.get()
    if language:
        session = object_session(target)
        if session:
            filters = {foreign_key_field: target.id, 'iso_639_1': language}
            translation = session.query(translation_model).filter_by(**filters).first()

            if translation:
                for attr in attributes:
                    setattr(target, attr, getattr(translation, attr))


class BaseMedia(Base):
    __abstract__ = True
    adult = Column(Boolean, nullable=False, comment='是否为成人')
    backdrop_path = Column(String, nullable=True, comment='背景图片路径')
    origin_country = Column(ARRAY(String), nullable=True, comment='原产国')
    status = Column(String, nullable=True, comment='状态')
    original_language = Column(String, nullable=False, comment='原语言')
    popularity = Column(Float, nullable=False, comment='流行度')
    poster_path = Column(String, nullable=True, comment='海报路径')
    vote_average = Column(Float, nullable=False, comment='平均评分')
    vote_count = Column(Integer, nullable=False, comment='评分人数')




class TMDBCast(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    people_id = Column(Integer, ForeignKey('tmdb_people.id'))
    character = Column(String, nullable=True, comment='角色')
    order = Column(Integer, nullable=True, comment='排序')
    credit_id = Column(String, nullable=True, comment='信用ID')
    cast_id = Column(Integer, nullable=True, comment='演员ID')


class TMDBCrew(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    people_id = Column(Integer, ForeignKey('tmdb_people.id'))
    department = Column(String, nullable=True, comment='部门')
    job = Column(String, nullable=True, comment='职务')
    credit_id = Column(String, nullable=True, comment='信用ID')


class TMDBImageTypeEnum(enum.Enum):
    backdrop = 'backdrop'
    logo = 'logo'
    poster = 'poster'


class TMDBImage(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(255), nullable=False)
    image_type = Column(Enum(TMDBImageTypeEnum), nullable=False)
    aspect_ratio = Column(Float, nullable=True)
    height = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    iso_639_1 = Column(String(2), nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)


class TMDBVideo(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    iso_639_1 = Column(String(2), nullable=False)
    iso_3166_1 = Column(String(2), nullable=False)
    name = Column(String(255), nullable=False)
    key = Column(String(255), nullable=False)
    site = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    official = Column(Boolean, nullable=False)
    published_at = Column(String, nullable=False)
    tmdb_video_id = Column(String(255), nullable=False)  # Renamed to avoid conflict with PK
