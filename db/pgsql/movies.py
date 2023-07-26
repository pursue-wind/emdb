import json

from sqlalchemy import cast, Integer
from sqlalchemy.dialects.postgresql import insert, ARRAY
from tornado import gen

from db.pgsql.mysql_models import Imgs, Movies, MovieKeyWords, ProductionCompany, MoviesCredits
from db.pgsql.base import exc_handler, datetime_handler


@gen.coroutine
@exc_handler
def query_movie_by_name(movie_name, **kwargs):
    sess = kwargs.get('sess')
    movie_list = sess.query(Movies).filter(Movies.original_title.ilike(f"%{movie_name}%")).all()
    # movie_list = [json.dumps(movie.to_dict(), default=datetime_handler) for movie in results]
    if len(movie_list) > 0:
        movie_list = [movie.to_dict() for movie in movie_list]

    return dict(movies=movie_list)

@gen.coroutine
@exc_handler
def query_movie_by_tmdb_id(tmdb_movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(Movies).filter(Movies.tmdb_id == tmdb_movie_id).first()
    if not results:
        return dict(movie_info=dict())
    movie = results.to_dict()
    return dict(movie_info=movie)


@gen.coroutine
@exc_handler
def query_movie_by_company_id(tmdb_company_id, **kwargs):
    sess = kwargs.get('sess')
    page_num = kwargs.get("page_num")
    page_size = kwargs.get("page_size")
    movie_name = kwargs.get("movie_name")
    query = sess.query(Movies).filter(Movies.production_companies.any(tmdb_company_id))
    if movie_name:
        query = query.filter(Movies.original_title.ilike(f"%{movie_name}%"))

    total = query.count()

    offset = (int(page_num) - 1) * int(page_size)
    movie_list = query.offset(offset).limit(page_size).all()
    _movie_list = []
    for movie in movie_list:
        movie = movie.to_dict()
        _movie_list.append(movie)
    return dict(movies=_movie_list, total=total,
                page_num=page_num, page_size=page_size)


@gen.coroutine
@exc_handler
def insert_movies(movie_info, **kwargs):
    sess = kwargs.get('sess')

    movie_data = {k: v for k, v in movie_info.items() if v is not None}
    movie = Movies(**movie_data)
    sess.add(movie)
    sess.commit()

    return dict(movie_id=movie.id)


@gen.coroutine
@exc_handler
def insert_movie_info(movie_info, key_words_list, production_company_list, credits,  **kwargs):
    """Query User Info."""
    sess = kwargs.get('sess')

    # movie info
    movie_data = {k: v for k, v in movie_info.items() if v is not None}
    movie = Movies(**movie_data)
    sess.add(movie)
    # sess.commit()

    # keywords
    key_words_list = [{"tmdb_id": d["id"], "name": d["name"], "movie_id": movie.id} for d in key_words_list]

    stmt = insert(MovieKeyWords).values(key_words_list).on_conflict_do_nothing()
    sess.execute(stmt)

    # production companies
    stmt = insert(ProductionCompany).values(production_company_list).on_conflict_do_nothing()
    sess.execute(stmt)

    # credits
    stmt = insert(MoviesCredits).values(credits).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()

    return dict(movie_id=movie.id)
