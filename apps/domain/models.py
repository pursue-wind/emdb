from datetime import datetime

from sqlalchemy import ForeignKey, Table, ARRAY, Column, Integer, String, Boolean, Float, Text, event, and_, DateTime, \
    TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import object_session, relationship

from apps.domain.base import TMDBCast, load_translation, BaseMedia, TMDBCrew, Base, TMDBImage, TMDBVideo, \
    load_translation_by_iso_639_1, IMAGE_BASE_URL, Base0
from apps.handlers.base import language_var

# Many-to-Many relationship tables for TMDBMovie
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


class TMDBCreatedBy(Base):
    __tablename__ = 'tmdb_created_by'

    id = Column(Integer, primary_key=True, autoincrement=False)
    credit_id = Column(String, nullable=False, comment='信用 ID')
    gender = Column(Integer, nullable=False, comment='性别')
    name = Column(String, nullable=False, comment='姓名')
    original_name = Column(String, nullable=False, comment='原名')
    profile_path = Column(String, nullable=True, comment='头像路径')

    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_created_by_table, back_populates='created_by')


class TMDBGenre(Base0):
    __tablename__ = 'tmdb_genres'

    id = Column(Integer, primary_key=True, autoincrement=False)
    # 在关系表中添加back_populates，以双向连接关系。
    movies = relationship('TMDBMovie', secondary=tmdb_movie_genres_table, back_populates='genres')
    tv_shows = relationship('TMDBTV', secondary=tmdb_tv_genres_table, back_populates='genres')
    translations = relationship('TMDBGenreTranslation', back_populates='genre')


class TMDBGenreTranslation(Base0):
    __tablename__ = 'tmdb_genres_translations'

    genre_id = Column(Integer, ForeignKey('tmdb_genres.id'), primary_key=True)
    language = Column(String, primary_key=True, comment='语言代码')
    name = Column(String, nullable=False, comment='名称')
    # 关系
    genre = relationship('TMDBGenre', back_populates='translations')


@event.listens_for(TMDBGenre, 'load')
def load_genre_translation(target, context):
    load_translation(
        target=target,
        context=context,
        translation_model=TMDBGenreTranslation,
        foreign_key_field='genre_id',
        attributes=['name']
    )


@event.listens_for(TMDBGenre, 'after_insert')
def insert_genre_translation(mapper, connection, target):
    language = language_var.get()
    if language:
        # 在插入之前，确保翻译数据也被插入
        translation = TMDBGenreTranslation(
            genre_id=target.id,
            language=language,
            name=target.name
        )
        session = object_session(target)
        if session:
            session.merge(translation)



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


class TMDBMovieTranslation(Base):
    __tablename__ = 'tmdb_movie_translations'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), nullable=False, comment='关联电影的ID', primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    iso_639_1 = Column(String(2), nullable=False, comment='语言的ISO 639-1代码', primary_key=True)
    name = Column(String, nullable=True, comment='语言的本地名称')
    english_name = Column(String, nullable=True, comment='语言的英语名称')
    homepage = Column(String, nullable=True, comment='翻译版本的主页URL')
    overview = Column(String, nullable=True, comment='翻译版本的概述')
    runtime = Column(Integer, nullable=True, comment='翻译版本的运行时长，以分钟为单位')
    tagline = Column(String, nullable=True, comment='翻译版本的标语')
    title = Column(String, nullable=True, comment='翻译版本的标题')

    movie = relationship("TMDBMovie", back_populates="translations")


class TMDBTVTranslation(Base):
    __tablename__ = 'tmdb_tv_translations'
    tv_id = Column(Integer, ForeignKey('tmdb_tv.id'), primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    iso_639_1 = Column(String(2), nullable=False, comment='语言的ISO 639-1代码', primary_key=True)
    lang_name = Column(String, nullable=True, comment='语言的本地名称')
    english_name = Column(String, nullable=True, comment='语言的英语名称')
    homepage = Column(String, nullable=True, comment='翻译版本的主页URL')
    overview = Column(String, nullable=True, comment='翻译版本的概述')
    tagline = Column(String, nullable=True, comment='翻译版本的标语')
    name = Column(String, nullable=True, comment='翻译版本的标题')
    # 关系
    tv_show = relationship('TMDBTV', back_populates='translations')


class TMDBTVSeasonTranslation(Base):
    __tablename__ = 'tmdb_tv_season_translations'

    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    iso_639_1 = Column(String(2), nullable=False, comment='语言的ISO 639-1代码', primary_key=True)
    lang_name = Column(String, nullable=True, comment='语言的本地名称')
    english_name = Column(String, nullable=True, comment='语言的英语名称')
    overview = Column(String, nullable=True, comment='翻译版本的概述')
    name = Column(String, nullable=True, comment='翻译版本的标题')
    # 关系
    tv_season = relationship('TMDBTVSeason', back_populates='translations')


class TMDBMovie(BaseMedia):
    __tablename__ = 'tmdb_movies'

    id = Column(Integer, primary_key=True, autoincrement=False)

    budget = Column(Integer, nullable=False, comment='预算')

    imdb_id = Column(String, nullable=True, comment='IMDb ID')

    original_title = Column(String, nullable=True, comment='原标题')

    release_date = Column(String, nullable=True, comment='上映日期')
    revenue = Column(Integer, nullable=False, comment='收入')
    runtime = Column(Integer, nullable=True, comment='时长（分钟）')
    homepage = Column(String, nullable=True, comment='主页URL')
    overview = Column(String, nullable=True, comment='概述')
    tagline = Column(String, nullable=True, comment='标语')
    title = Column(String, nullable=True, comment='标题')
    video = Column(Boolean, nullable=False, comment='是否为视频')
    belongs_to_collection = Column(JSONB, nullable=True, comment='belongs_to_collection，作为JSON数组存储')

    genres = relationship('TMDBGenre', secondary=lambda: tmdb_movie_genres_table, back_populates='movies')

    spoken_languages = relationship('TMDBSpokenLanguage', secondary=lambda: tmdb_movie_spoken_languages_table,
                                    back_populates='movies')
    production_companies = relationship('TMDBProductionCompany',
                                        secondary=lambda: tmdb_movie_production_companies_table,
                                        back_populates='movies')
    production_countries = relationship('TMDBProductionCountry',
                                        secondary=lambda: tmdb_movie_production_countries_table,
                                        back_populates='movies')
    # 关系
    movie_cast = relationship('TMDBMovieCast', back_populates='movie')
    movie_crew = relationship('TMDBMovieCrew', back_populates='movie')
    translations = relationship('TMDBMovieTranslation', back_populates='movie')
    images = relationship('TMDBMovieImage', back_populates='movie')
    videos = relationship('TMDBMovieVideo', back_populates='movie')

    release_dates = relationship('TMDBMovieReleaseDate', back_populates='movie')
    alternative_titles = relationship('TMDBMovieAlternativeTitle', back_populates='movie')


class TMDBMovieReleaseDate(Base):
    __tablename__ = 'tmdb_movie_release_dates'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), nullable=False, comment='关联电影的ID', primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    certification = Column(String, nullable=True, comment='电影在该国的分级认证')
    descriptors = Column(JSONB, nullable=True, comment='描述符，作为JSON数组存储')
    iso_639_1 = Column(String(2), nullable=True, comment='语言的ISO 639-1代码', primary_key=True)
    note = Column(String, nullable=True, comment='有关发行的备注')
    release_date = Column(TIMESTAMP(timezone=True), nullable=False, comment='电影的发行日期和时间')
    type = Column(Integer, nullable=False, comment='发行类型的标识符')

    movie = relationship('TMDBMovie', back_populates='release_dates')


class TMDBMovieAlternativeTitle(Base):
    __tablename__ = 'tmdb_movie_alternative_titles'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), nullable=False, comment='关联电影的ID', primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    title = Column(String, nullable=False, comment='电影的替代标题')
    type = Column(String, nullable=True, comment='替代标题的类型')

    movie = relationship('TMDBMovie', back_populates='alternative_titles')


class TMDBTVAlternativeTitle(Base):
    __tablename__ = 'tmdb_tv_alternative_titles'

    tv_id = Column(Integer, ForeignKey('tmdb_tv.id'), nullable=False, comment='关联TV的ID', primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    title = Column(String, nullable=False, comment='电影的替代标题')
    type = Column(String, nullable=True, comment='替代标题的类型')

    tv = relationship('TMDBTV', back_populates='alternative_titles')


class TMDBMovieImage(TMDBImage):
    __tablename__ = 'tmdb_movie_images'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), nullable=False)
    # 关系
    movie = relationship('TMDBMovie', back_populates='images')

    @staticmethod
    def build(movie_id, image_type, d: dict):
        d['movie_id'] = movie_id
        d['image_type'] = image_type
        return d


@event.listens_for(TMDBMovieImage, 'load')
def load_movie_img(target, context):
    # 兼容emmai之前的接口
    if target.file_path:
        target.url = IMAGE_BASE_URL + target.file_path


class TMDBTVImage(TMDBImage):
    __tablename__ = 'tmdb_tv_images'

    tv_id = Column(Integer, ForeignKey('tmdb_tv.id'), nullable=False)
    tv = relationship('TMDBTV', back_populates='images')

    @staticmethod
    def build(movie_id, image_type, d: dict):
        d['tv_id'] = movie_id
        d['image_type'] = image_type
        return d


@event.listens_for(TMDBTVImage, 'load')
def load_tv_img(target, context):
    # 兼容emmai之前的接口
    if target.file_path:
        target.url = IMAGE_BASE_URL + target.file_path


class TMDBMovieVideo(TMDBVideo):
    __tablename__ = 'tmdb_movie_videos'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), nullable=False, primary_key=True)
    movie = relationship('TMDBMovie', back_populates='videos')

    @staticmethod
    def build(mid, d: dict):
        d['published_at'] = datetime.fromisoformat(d['published_at'].replace('Z', '+00:00'))
        d['movie_id'] = mid
        d['tmdb_video_id'] = d['id']
        return d


@event.listens_for(TMDBMovieVideo, 'load')
def load_video(target, context):
    # 兼容emmai之前的接口
    target.tmdb_id = target.tmdb_video_id
    if target.site == "YouTube":
        target.url = "https://www.youtube.com/watch?v=" + target.key


class TMDBTVVideo(TMDBVideo):
    __tablename__ = 'tmdb_tv_videos'

    tv_id = Column(Integer, ForeignKey('tmdb_tv.id'), nullable=False, primary_key=True)
    tv = relationship('TMDBTV', back_populates='videos')

    @staticmethod
    def build(mid, d: dict):
        d['published_at'] = datetime.fromisoformat(d['published_at'].replace('Z', '+00:00'))
        d['tv_id'] = mid
        d['tmdb_video_id'] = d['id']
        return d


@event.listens_for(TMDBTVVideo, 'load')
def load_tv_video(target, context):
    # 兼容emmai之前的接口
    target.tmdb_id = target.tmdb_video_id
    if target.site == "YouTube":
        target.url = "https://www.youtube.com/watch?v=" + target.key


@event.listens_for(TMDBMovie, 'load')
def load_movie_translation(target, context):
    load_translation_by_iso_639_1(
        target=target,
        context=context,
        translation_model=TMDBMovieTranslation,
        foreign_key_field='movie_id',
        attributes=['title', 'overview', 'tagline', 'homepage']
    )


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
    tv_episode_guest_star = relationship('TMDBTVEpisodeGuestStar', back_populates='people')
    tv_season_crew = relationship('TMDBTVSeasonCrew', back_populates='people')
    tv_season_cast = relationship('TMDBTVSeasonCast', back_populates='people')



class TMDBTV(BaseMedia):
    __tablename__ = 'tmdb_tv'

    id = Column(Integer, primary_key=True, autoincrement=False)

    episode_run_time = Column(ARRAY(Integer), nullable=False, comment='每集时长')
    first_air_date = Column(String, nullable=True, comment='首播日期')
    in_production = Column(Boolean, nullable=False, comment='是否在制作中')
    languages = Column(ARRAY(String), nullable=False, comment='语言')
    last_air_date = Column(String, nullable=True, comment='最近播放日期')
    homepage = Column(String, nullable=True, comment='主页URL')
    overview = Column(String, nullable=True, comment='概述')
    tagline = Column(String, nullable=True, comment='标语')
    name = Column(String, nullable=True, comment='标题')
    next_episode_to_air = Column(JSONB, nullable=True, comment='下一集')
    number_of_episodes = Column(Integer, nullable=False, comment='集数')
    number_of_seasons = Column(Integer, nullable=False, comment='季数')
    original_name = Column(String, nullable=True, comment='原名称')
    type = Column(String, nullable=True, comment='类型')
    created_by = relationship('TMDBCreatedBy', secondary=lambda: tmdb_tv_created_by_table,
                              back_populates='tv_shows')
    last_episode_to_air = Column(JSONB, nullable=True, comment='last_episode_to_air，作为JSON数组存储')
    networks = Column(JSONB, nullable=True, comment='networks，作为JSON数组存储')

    genres = relationship('TMDBGenre', secondary=lambda: tmdb_tv_genres_table, back_populates='tv_shows')

    production_companies = relationship('TMDBProductionCompany',
                                        secondary=lambda: tmdb_tv_production_companies_table,
                                        back_populates='tv_shows')
    production_countries = relationship('TMDBProductionCountry',
                                        secondary=lambda: tmdb_tv_production_countries_table,
                                        back_populates='tv_shows')
    alternative_titles = relationship('TMDBTVAlternativeTitle', back_populates='tv')
    seasons = relationship('TMDBTVSeason', back_populates='tv_show')
    spoken_languages = relationship('TMDBSpokenLanguage', secondary=lambda: tmdb_tv_spoken_languages_table,
                                    back_populates='tv_shows')
    translations = relationship('TMDBTVTranslation', back_populates='tv_show')
    images = relationship('TMDBTVImage', back_populates='tv')
    videos = relationship('TMDBTVVideo', back_populates='tv')


@event.listens_for(TMDBTV, 'load')
def load_tv_translation(target, context):
    target.tmdb_id = target.id
    load_translation_by_iso_639_1(
        target=target,
        context=context,
        translation_model=TMDBTVTranslation,
        foreign_key_field='tv_id',
        attributes=['name', 'overview', 'tagline', 'homepage']
    )


class TMDBTVSeason(Base):
    __tablename__ = 'tmdb_tv_seasons'

    id = Column(Integer, primary_key=True, autoincrement=False)
    overview = Column(String, nullable=True, comment='概述')
    name = Column(String, nullable=True, comment='标题')
    air_date = Column(String, nullable=True, comment='播放日期')
    episode_count = Column(Integer, nullable=True, comment='集数')
    poster_path = Column(String, nullable=True, comment='海报路径')
    season_number = Column(Integer, nullable=False, comment='季数')
    vote_average = Column(Float, nullable=False, comment='平均评分')
    tv_show_id = Column(Integer, ForeignKey('tmdb_tv.id'), nullable=False)
    tv_show = relationship('TMDBTV', back_populates='seasons')
    episodes = relationship('TMDBTVEpisode', backref='tv_season', cascade='all, delete-orphan')
    # 关系
    tv_season_cast = relationship('TMDBTVSeasonCast', back_populates='tv_season')
    tv_season_crew = relationship('TMDBTVSeasonCrew', back_populates='tv_season')
    translations = relationship('TMDBTVSeasonTranslation', back_populates='tv_season')


@event.listens_for(TMDBTVSeason, 'load')
def load_tv_season_translation(target, context):
    load_translation_by_iso_639_1(
        target=target,
        context=context,
        translation_model=TMDBTVSeasonTranslation,
        foreign_key_field='tv_season_id',
        attributes=['name', 'overview']
    )


class TMDBTVEpisode(Base):
    __tablename__ = 'tmdb_tv_episodes'

    id = Column(Integer, primary_key=True)
    overview = Column(String, nullable=True, comment='概述')
    name = Column(String, nullable=True, comment='标题')
    air_date = Column(String, nullable=True, comment='播放日期')
    episode_number = Column(Integer, nullable=True, comment='集数')
    episode_type = Column(String, nullable=True, comment='类型')
    production_code = Column(String, nullable=True, comment='制作代码')
    runtime = Column(Integer, nullable=True, comment='时长（分钟）')
    season_number = Column(Integer, nullable=True, comment='季数')
    show_id = Column(Integer, nullable=True, comment='剧集 ID')
    vote_average = Column(Integer, nullable=True, comment='平均评分')
    vote_count = Column(Integer, nullable=True, comment='评分人数')
    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), nullable=False)
    # 关系
    tv_episode_cast = relationship('TMDBTVEpisodeCast', back_populates='tv_episode')
    tv_episode_guest_star = relationship('TMDBTVEpisodeGuestStar', back_populates='tv_episode')
    tv_episode_crew = relationship('TMDBTVEpisodeCrew', back_populates='tv_episode')
    translations = relationship('TMDBTVEpisodeTranslation', back_populates='tv_episode')


class TMDBTVEpisodeTranslation(Base):
    __tablename__ = 'tmdb_tv_episodes_translations'
    tv_episode_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), primary_key=True)
    iso_3166_1 = Column(String(2), nullable=False, comment='国家的ISO 3166-1代码', primary_key=True)
    iso_639_1 = Column(String(2), nullable=False, comment='语言的ISO 639-1代码', primary_key=True)
    lang_name = Column(String, nullable=True, comment='语言的本地名称')
    english_name = Column(String, nullable=True, comment='语言的英语名称')
    overview = Column(String, nullable=True, comment='翻译版本的概述')
    name = Column(String, nullable=True, comment='翻译版本的标题')
    # 关系
    tv_episode = relationship('TMDBTVEpisode', back_populates='translations')


@event.listens_for(TMDBTVEpisode, 'load')
def load_tv_episode_translation(target, context):
    load_translation_by_iso_639_1(
        target=target,
        context=context,
        translation_model=TMDBTVEpisodeTranslation,
        foreign_key_field='tv_episode_id',
        attributes=['name', 'overview']
    )


#############

class TMDBTVEpisodeGuestStar(TMDBCast):
    __tablename__ = 'tmdb_tv_episode_guest_stars'

    tv_episode_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), primary_key=True)
    tv_episode = relationship('TMDBTVEpisode', back_populates='tv_episode_guest_star')
    people = relationship('TMDBPeople', back_populates='tv_episode_guest_star')



##################


class TMDBMovieCrew(TMDBCrew):
    __tablename__ = 'tmdb_movie_crews'
    people = relationship('TMDBPeople', back_populates='movie_crew')
    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), primary_key=True)
    # 关系
    movie = relationship('TMDBMovie', back_populates='movie_crew')


class TMDBTVEpisodeCrew(TMDBCrew):
    __tablename__ = 'tmdb_tv_episode_crews'
    people = relationship('TMDBPeople', back_populates='tv_episode_crew')
    tv_episode_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), nullable=False, primary_key=True)
    # 关系
    tv_episode = relationship('TMDBTVEpisode', back_populates='tv_episode_crew')


class TMDBTVSeasonCrew(TMDBCrew):
    __tablename__ = 'tmdb_tv_season_crews'
    people = relationship('TMDBPeople', back_populates='tv_season_crew')
    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), nullable=False, primary_key=True)
    # 关系
    tv_season = relationship('TMDBTVSeason', back_populates='tv_season_crew')


#############
class TMDBMovieCast(TMDBCast):
    __tablename__ = 'tmdb_movie_cast'

    movie_id = Column(Integer, ForeignKey('tmdb_movies.id'), primary_key=True)
    # 关系
    movie = relationship('TMDBMovie', back_populates='movie_cast')
    people = relationship('TMDBPeople', back_populates='movie_cast')


class TMDBTVEpisodeCast(TMDBCast):
    __tablename__ = 'tmdb_tv_episodes_crew'

    tv_episodes_id = Column(Integer, ForeignKey('tmdb_tv_episodes.id'), primary_key=True)
    # 关系
    tv_episode = relationship('TMDBTVEpisode', back_populates='tv_episode_cast')
    people = relationship('TMDBPeople', back_populates='tv_episode_cast')


class TMDBTVSeasonCast(TMDBCast):
    __tablename__ = 'tmdb_tv_season_cast'

    tv_season_id = Column(Integer, ForeignKey('tmdb_tv_seasons.id'), primary_key=True)
    # 关系
    tv_season = relationship('TMDBTVSeason', back_populates='tv_season_cast')
    people = relationship('TMDBPeople', back_populates='tv_season_cast')
