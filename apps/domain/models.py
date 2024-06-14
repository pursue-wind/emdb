from sqlalchemy import ForeignKey, Table, ARRAY, create_engine, \
    Column, Integer, String, Boolean, Float, Text, event
from sqlalchemy.orm import object_session, relationship, sessionmaker, declarative_base

from apps.handlers.base import language_var

Base = declarative_base()

# Many-to-Many relationship tables for TMDBMovie
tmdb_movie_created_by_table = Table(
    'tmdb_movie_created_by', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'), primary_key=True),
    Column('created_by_id', Integer, ForeignKey('tmdb_created_by.id'),
           primary_key=True),
)

tmdb_movie_genres_table = Table(
    'tmdb_movie_genres', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('tmdb_genres.id'), primary_key=True),
)

tmdb_movie_networks_table = Table(
    'tmdb_movie_networks', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'), primary_key=True),
    Column('network_id', Integer, ForeignKey('tmdb_networks.id'), primary_key=True),
)

tmdb_movie_production_companies_table = Table(
    'tmdb_movie_production_companies', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'),
           primary_key=True),
    Column('production_company_id', Integer,
           ForeignKey('tmdb_production_companies.id'), primary_key=True),
)

tmdb_movie_production_countries_table = Table(
    'tmdb_movie_production_countries', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'),
           primary_key=True),
    Column('production_country_id', String,
           ForeignKey('tmdb_production_countries.iso_3166_1'),
           primary_key=True),
)

tmdb_movie_spoken_languages_table = Table(
    'tmdb_movie_spoken_languages', Base.metadata,
    Column('movie_id', Integer, ForeignKey('tmdb_movies.id'), primary_key=True),
    Column('spoken_language_id', String,
           ForeignKey('tmdb_spoken_languages.iso_639_1'), primary_key=True),
)

# Many-to-Many relationship tables for TMDBTV
tmdb_tv_created_by_table = Table(
    'tmdb_tv_created_by', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('created_by_id', Integer, ForeignKey('tmdb_created_by.id'), primary_key=True),
)

tmdb_tv_genres_table = Table(
    'tmdb_tv_genres', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('tmdb_genres.id'), primary_key=True),
)

tmdb_tv_networks_table = Table(
    'tmdb_tv_networks', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('network_id', Integer, ForeignKey('tmdb_networks.id'), primary_key=True),
)

tmdb_tv_production_companies_table = Table(
    'tmdb_tv_production_companies', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('production_company_id', Integer,
           ForeignKey('tmdb_production_companies.id'), primary_key=True),
)

tmdb_tv_production_countries_table = Table(
    'tmdb_tv_production_countries', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('production_country_id', String,
           ForeignKey('tmdb_production_countries.iso_3166_1'), primary_key=True),
)

tmdb_tv_spoken_languages_table = Table(
    'tmdb_tv_spoken_languages', Base.metadata,
    Column('tv_id', Integer, ForeignKey('tmdb_tv.id'), primary_key=True),
    Column('spoken_language_id', String,
           ForeignKey('tmdb_spoken_languages.iso_639_1'), primary_key=True),
)


#############
class TMDBCast(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    people_id = Column(Integer, ForeignKey('tmdb_people.id'))
    character = Column(String, nullable=True, comment='角色')
    order = Column(Integer, nullable=True, comment='排序')
    credit_id = Column(String, nullable=True, comment='信用ID')
    cast_id = Column(Integer, nullable=True, comment='演员ID')


class TMDBMovieCast(TMDBCast):
    __tablename__ = 'tmdb_movie_cast'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'))
    # 关系
    movie = relationship('TMDBMovie', back_populates='movie_cast')
    people = relationship('TMDBPeople', back_populates='movie_cast')


class TMDBTVEpisodeCast(TMDBCast):
    __tablename__ = 'tmdb_tv_episodes_crew'

    tv_episodes_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'))
    # 关系
    tv_episode = relationship('TMDBTVEpisode', back_populates='tv_episode_cast')
    people = relationship('TMDBPeople', back_populates='tv_episode_cast')


class TMDBTVSeasonCast(TMDBCast):
    __tablename__ = 'tmdb_tv_season_crew'

    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'))
    # 关系
    tv_season = relationship('TMDBTVSeason', back_populates='tv_season_cast')
    people = relationship('TMDBPeople', back_populates='tv_season_cast')


class TMDBCreatedBy(Base):
    __tablename__ = 'tmdb_created_by'

    id = Column(Integer, primary_key=True, autoincrement=False)
    credit_id = Column(String, nullable=False, comment='信用 ID')
    gender = Column(Integer, nullable=False, comment='性别')
    name = Column(String, nullable=False, comment='姓名')
    original_name = Column(String, nullable=False, comment='原名')
    profile_path = Column(String, nullable=True, comment='头像路径')

    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_created_by_table, back_populates='created_by')


class TMDBGenre(Base):
    __tablename__ = 'tmdb_genres'

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False, comment='名称')
    # 在关系表中添加back_populates，以双向连接关系。
    movies = relationship('TMDBMovie', secondary=tmdb_movie_genres_table, back_populates='genres')
    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_genres_table, back_populates='genres')


class TMDBNetwork(Base):
    __tablename__ = 'tmdb_networks'

    id = Column(Integer, primary_key=True, autoincrement=False)
    logo_path = Column(String, nullable=True, comment='标志路径')
    name = Column(String, nullable=False, comment='名称')
    origin_country = Column(String, nullable=False, comment='原产国')

    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_networks_table, back_populates='networks')


class TMDBProductionCompany(Base):
    __tablename__ = 'tmdb_production_companies'

    id = Column(Integer, primary_key=True, autoincrement=False)
    logo_path = Column(String, nullable=True, comment='标志路径')
    name = Column(String, nullable=True, comment='名称')
    origin_country = Column(String, nullable=True, comment='原产国')

    movies = relationship('TMDBMovie', secondary=tmdb_movie_production_companies_table,
                          back_populates='production_companies')
    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_production_companies_table,
                            back_populates='production_companies')


class TMDBProductionCountry(Base):
    __tablename__ = 'tmdb_production_countries'

    iso_3166_1 = Column(String, primary_key=True, comment='ISO 3166-1')
    name = Column(String, nullable=True, comment='名称')
    movies = relationship('TMDBMovie', secondary=tmdb_movie_production_countries_table,
                          back_populates='production_countries')
    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_production_countries_table,
                            back_populates='production_countries')


class TMDBSpokenLanguage(Base):
    __tablename__ = 'tmdb_spoken_languages'

    iso_639_1 = Column(String, primary_key=True, comment='ISO 639-1')
    english_name = Column(String, nullable=True, comment='英文名称')
    name = Column(String, nullable=True, comment='本地名称')

    movies = relationship('TMDBMovie', secondary=tmdb_movie_spoken_languages_table,
                          back_populates='spoken_languages')
    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_spoken_languages_table,
                            back_populates='spoken_languages')


class TMDBBelongsToCollection(Base):
    __tablename__ = 'tmdb_belongs_to_collections'

    id = Column(Integer, primary_key=True)
    backdrop_path = Column(String, nullable=True)
    name = Column(String, nullable=True)
    poster_path = Column(String, nullable=True)


class TMDBMovieTranslation(Base):
    __tablename__ = 'tmdb_movie_translations'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), primary_key=True)
    language = Column(String, primary_key=True, comment='语言代码')
    title = Column(String, nullable=False, comment='标题')
    overview = Column(Text, nullable=False, comment='概述')
    tagline = Column(String, nullable=False, comment='标语')
    homepage = Column(String, nullable=False, comment='首页')
    # 关系
    movie = relationship('TMDBMovie', back_populates='translations')


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


class TMDBMovie(BaseMedia):
    __tablename__ = 'tmdb_movies'

    id = Column(Integer, primary_key=True, autoincrement=False)
    belongs_to_collection_id = Column(Integer, ForeignKey('tmdb_belongs_to_collections.id'))
    belongs_to_collection = relationship('TMDBBelongsToCollection', backref='tmdb_movies')
    budget = Column(Integer, nullable=False, comment='预算')
    genres = relationship('TMDBGenre', secondary=lambda: tmdb_movie_genres_table, back_populates='movies')

    imdb_id = Column(String, nullable=True, comment='IMDb ID')

    original_title = Column(String, nullable=True, comment='原标题')

    production_companies = relationship('TMDBProductionCompany',
                                        secondary=lambda: tmdb_movie_production_companies_table,
                                        back_populates='movies')
    production_countries = relationship('TMDBProductionCountry',
                                        secondary=lambda: tmdb_movie_production_countries_table,
                                        back_populates='movies')
    release_date = Column(String, nullable=True, comment='上映日期')
    revenue = Column(Integer, nullable=False, comment='收入')
    runtime = Column(Integer, nullable=True, comment='时长（分钟）')
    spoken_languages = relationship('TMDBSpokenLanguage', secondary=lambda: tmdb_movie_spoken_languages_table,
                                    back_populates='movies')
    video = Column(Boolean, nullable=False, comment='是否为视频')

    # 关系
    movie_cast = relationship('TMDBMovieCast', back_populates='movie')
    movie_crew = relationship('TMDBMovieCrew', back_populates='movie')
    translations = relationship('TMDBMovieTranslation', back_populates='movie')


@event.listens_for(TMDBMovie, 'load')
def load_movie_translation(target, context):
    # 获取所需的语言
    language = language_var.get()
    if language:
        session = object_session(target)
        if session:
            # 从数据库中查询所需语言的翻译
            translation = session.query(TMDBMovieTranslation).filter_by(
                movie_id=target.id, language=language
            ).first()

            # 如果找到翻译，将其属性应用于目标对象
            if translation:
                for attr in ['title', 'overview', 'tagline', 'homepage']:
                    setattr(target, attr, getattr(translation, attr))


class TMDBPeople(Base):
    __tablename__ = 'tmdb_people'

    id = Column(Integer, primary_key=True, autoincrement=False)
    adult = Column(Boolean, nullable=False, comment='是否为成人')
    biography = Column(Text, nullable=True, comment='传记')
    birthday = Column(String, nullable=True, comment='生日')
    deathday = Column(String, nullable=True, comment='死亡日期')
    gender = Column(Integer, nullable=False, comment='性别')
    homepage = Column(String, nullable=True, comment='首页')
    imdb_id = Column(String, nullable=True, comment='IMDb ID')
    known_for_department = Column(String, nullable=True, comment='知名部门')
    name = Column(String, nullable=False, comment='名字')
    place_of_birth = Column(String, nullable=True, comment='出生地')
    popularity = Column(Float, nullable=False, comment='流行度')
    profile_path = Column(String, nullable=True, comment='头像路径')
    also_known_as = Column(ARRAY(String), nullable=True, comment='别名')

    # 关系
    movie_cast = relationship('TMDBMovieCast', back_populates='people')
    movie_crew = relationship('TMDBMovieCrew', back_populates='people')
    tv_episode_crew = relationship('TMDBTVEpisodeCrew', back_populates='people')
    tv_episode_cast = relationship('TMDBTVEpisodeCast', back_populates='people')
    tv_season_crew = relationship('TMDBTVSeasonCrew', back_populates='people')
    tv_season_cast = relationship('TMDBTVSeasonCast', back_populates='people')


class TMDBTV(BaseMedia):
    __tablename__ = 'tmdb_tv'

    id = Column(Integer, primary_key=True, autoincrement=False)
    created_by = relationship('TMDBCreatedBy', secondary=lambda: tmdb_tv_created_by_table, back_populates='tv_shows')
    episode_run_time = Column(ARRAY(Integer), nullable=False, comment='每集时长')
    first_air_date = Column(String, nullable=True, comment='首播日期')
    genres = relationship('TMDBGenre', secondary=lambda: tmdb_tv_genres_table, back_populates='tv_shows')
    in_production = Column(Boolean, nullable=False, comment='是否在制作中')
    languages = Column(ARRAY(String), nullable=False, comment='语言')
    last_air_date = Column(String, nullable=True, comment='最近播放日期')
    last_episode_to_air_id = Column(Integer, ForeignKey('tmdb_last_episode_to_air.id'))
    last_episode_to_air = relationship('TMDBLastEpisodeToAir')
    name = Column(String, nullable=False, comment='名称')
    next_episode_to_air = Column(String, nullable=True, comment='下一集')
    number_of_episodes = Column(Integer, nullable=False, comment='集数')
    number_of_seasons = Column(Integer, nullable=False, comment='季数')
    original_name = Column(String, nullable=True, comment='原名称')
    title = Column(String, nullable=True, comment='标题')
    type = Column(String, nullable=True, comment='类型')
    networks = relationship('TMDBNetwork', secondary=lambda: tmdb_tv_networks_table, back_populates='tv_shows')

    production_companies = relationship('TMDBProductionCompany', secondary=lambda: tmdb_tv_production_companies_table,
                                        back_populates='tv_shows')
    production_countries = relationship('TMDBProductionCountry', secondary=lambda: tmdb_tv_production_countries_table,
                                        back_populates='tv_shows')
    seasons = relationship('TMDBTVSeason', back_populates='tv_show')
    spoken_languages = relationship('TMDBSpokenLanguage', secondary=lambda: tmdb_tv_spoken_languages_table,
                                    back_populates='tv_shows')


class TMDBTVSeason(Base):
    __tablename__ = 'tmdb_tv_seasons'

    id = Column(Integer, primary_key=True, autoincrement=False)
    air_date = Column(String, nullable=True, comment='播放日期')
    episode_count = Column(Integer, nullable=True, comment='集数')
    name = Column(String, nullable=False, comment='名称')
    overview = Column(Text, nullable=False, comment='概述')
    poster_path = Column(String, nullable=True, comment='海报路径')
    season_number = Column(Integer, nullable=False, comment='季数')
    vote_average = Column(Float, nullable=False, comment='平均评分')
    tv_show_id = Column(Integer, ForeignKey('tmdb_tv.id'), nullable=False)
    tv_show = relationship('TMDBTV', back_populates='seasons')
    episodes = relationship('TMDBTVEpisode', backref='tv_season', cascade='all, delete-orphan')
    # 关系
    tv_season_cast = relationship('TMDBTVSeasonCast', back_populates='tv_season')
    tv_season_crew = relationship('TMDBTVSeasonCrew', back_populates='tv_season')


class TMDBTVEpisode(Base):
    __tablename__ = 'tmdb_tv_episodes'

    id = Column(Integer, primary_key=True)
    air_date = Column(String, nullable=True, comment='播放日期')
    episode_number = Column(Integer, nullable=True, comment='集数')
    episode_type = Column(String, nullable=True, comment='类型')
    name = Column(String, nullable=True, comment='名称')
    overview = Column(Text, nullable=True, comment='概述')
    production_code = Column(String, nullable=True, comment='制作代码')
    runtime = Column(Integer, nullable=True, comment='时长（分钟）')
    season_number = Column(Integer, nullable=True, comment='季数')
    show_id = Column(Integer, nullable=True, comment='剧集 ID')
    vote_average = Column(Integer, nullable=True, comment='平均评分')
    vote_count = Column(Integer, nullable=True, comment='评分人数')
    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), nullable=False)
    # 关系
    guest_stars = relationship('TMDBGuestStar', backref='tv_episode')
    tv_episode_cast = relationship('TMDBTVEpisodeCast', back_populates='tv_episode')
    tv_episode_crew = relationship('TMDBTVEpisodeCrew', back_populates='tv_episode')


class TMDBLastEpisodeToAir(Base):
    __tablename__ = 'tmdb_last_episode_to_air'

    id = Column(Integer, primary_key=True, autoincrement=False)
    air_date = Column(String, nullable=False, comment='播放日期')
    episode_number = Column(Integer, nullable=False, comment='集数')
    episode_type = Column(String, nullable=False, comment='类型')
    name = Column(String, nullable=False, comment='名称')
    overview = Column(Text, nullable=False, comment='概述')
    production_code = Column(String, nullable=False, comment='制作代码')
    runtime = Column(Integer, nullable=False, comment='时长（分钟）')
    season_number = Column(Integer, nullable=False, comment='季数')
    show_id = Column(Integer, nullable=False, comment='剧集 ID')
    still_path = Column(String, nullable=True, comment='静态图片路径')
    vote_average = Column(Float, nullable=False, comment='平均评分')
    vote_count = Column(Integer, nullable=False, comment='评分人数')


#############

class TMDBGuestStar(Base):
    __tablename__ = 'tmdb_guest_stars'

    id = Column(Integer, primary_key=True)
    credit_id = Column(String, nullable=False, comment='信用 ID')
    character = Column(String, nullable=False, comment='角色')
    name = Column(String, nullable=False, comment='姓名')
    original_name = Column(String, nullable=False, comment='原名')
    gender = Column(Integer, nullable=False, comment='性别')
    adult = Column(Boolean, nullable=False, comment='是否成人')
    order = Column(Integer, nullable=False, comment='顺序')
    known_for_department = Column(String, nullable=False, comment='知名部门')
    popularity = Column(Integer, nullable=False, comment='流行度')
    profile_path = Column(String, nullable=True, comment='头像路径')
    tv_episode_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), nullable=False)


##################
class TMDBCrew(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    people_id = Column(Integer, ForeignKey('tmdb_people.id'))
    department = Column(String, nullable=True, comment='部门')
    job = Column(String, nullable=True, comment='职务')
    credit_id = Column(String, nullable=True, comment='信用ID')


class TMDBMovieCrew(TMDBCrew):
    __tablename__ = 'tmdb_movie_crews'
    people = relationship('TMDBPeople', back_populates='movie_crew')
    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'))
    # 关系
    movie = relationship('TMDBMovie', back_populates='movie_crew')


class TMDBTVEpisodeCrew(TMDBCrew):
    __tablename__ = 'tmdb_tv_episode_crews'
    people = relationship('TMDBPeople', back_populates='tv_episode_crew')
    tv_episode_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), nullable=False)
    # 关系
    tv_episode = relationship('TMDBTVEpisode', back_populates='tv_episode_crew')


class TMDBTVSeasonCrew(TMDBCrew):
    __tablename__ = 'tmdb_tv_season_crews'
    people = relationship('TMDBPeople', back_populates='tv_season_crew')
    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), nullable=False)
    # 关系
    tv_season = relationship('TMDBTVSeason', back_populates='tv_season_crew')


