# 创建引擎和会话
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.domain.models import TMDBMovieTranslation, TMDBMovie, Base

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# 创建表
Base.metadata.create_all(engine)

# 插入数据
original_movie = TMDBMovie(
    id=1,
    title='Original Movie',
    original_title='Original Movie',
    budget=1000000,
    release_date='2024-01-01',
    revenue=5000000,
    runtime=120,
    video=False,
    language='en'
)
session.add(original_movie)

translated_movie_en = TMDBMovieTranslation(
    movie_id=1,
    language='en',
    title='Original Movie',
    overview='Original overview in English',
    tagline='Original tagline in English',
    homepage='http://original.example.com'
)
translated_movie_fr = TMDBMovieTranslation(
    movie_id=1,
    language='fr',
    title='Film Traduit',
    overview='Aperçu traduit en français',
    tagline='Slogan traduit en français',
    homepage='http://traduit.example.com'
)
session.add(translated_movie_en)
session.add(translated_movie_fr)

session.commit()

# 查询数据
def query_movie(language=None):
    movie = session.query(TMDBMovie).filter_by(id=1).one()
    movie.current_language = language
    return movie

# 使用不同语言查询
movie_en = query_movie(language='en')
print(f'ID: {movie_en.id}, Title: {movie_en.translated_title}, Overview: {movie_en.overview}, Tagline: {movie_en.tagline}, Homepage: {movie_en.homepage}')

movie_fr = query_movie(language='fr')
print(f'ID: {movie_fr.id}, Title: {movie_fr.translated_title}, Overview: {movie_fr.overview}, Tagline: {movie_fr.tagline}, Homepage: {movie_fr.homepage}')

movie_no_translation = query_movie(language='es')
print(f'ID: {movie_no_translation.id}, Title: {movie_no_translation.translated_title}, Overview: {movie_no_translation.overview}, Tagline: {movie_no_translation.tagline}, Homepage: {movie_no_translation.homepage}')
