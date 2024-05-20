import json
from operator import or_

from sqlalchemy import cast, Integer, and_, func
from sqlalchemy.dialects.postgresql import insert, ARRAY
from tornado import gen

from db.pgsql.enums.enums import SourceType
from db.pgsql.mysql_models import Imgs, Movies, MovieKeyWords, ProductionCompany, MoviesCredits, MovieAlternativeTitles
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
def query_movie_by_tmdb_id(tmdb_movie_id, source_type, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(Movies).filter(Movies.tmdb_id == tmdb_movie_id,
                                        Movies.source_type == source_type).first()
    if not results:
        return dict(movie_info=dict())
    movie = results.to_dict()
    return dict(movie_info=movie)


@gen.coroutine
@exc_handler
def count_movies_of_company(tmdb_company_id, source_type, **kwargs):
    sess = kwargs.get("sess")
    total_count = sess.query(func.count(Movies.id)).filter(
        and_(Movies.source_type == source_type, Movies.production_companies.any(tmdb_company_id))).scalar()
    if total_count is None:
        total_count = 0
    return dict(total_count=total_count)



@gen.coroutine
@exc_handler
def query_movie_by_company_id(tmdb_company_id, source_type, **kwargs):
    sess = kwargs.get('sess')
    page_num = kwargs.get("page_num")
    page_size = kwargs.get("page_size")
    movie_name = kwargs.get("movie_name")
    query = sess.query(Movies).outerjoin(MovieAlternativeTitles, Movies.id == MovieAlternativeTitles.movie_id).filter(
        and_(Movies.source_type == source_type,
             Movies.production_companies.any(tmdb_company_id)
             ))
    if movie_name:
        query = query.filter(or_(or_(Movies.original_title.ilike(f"%{movie_name}%"),
                                 Movies.title.ilike(f"%{movie_name}")),
                                 MovieAlternativeTitles.title.ilike(f"%{movie_name}%")))

    total = query.distinct().count()

    offset = (int(page_num) - 1) * int(page_size)
    movie_list = query.offset(offset).limit(page_size).distinct().all()
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
    existing_movie = sess.query(Movies).filter(Movies.tmdb_id == movie_info['tmdb_id'],
                                               Movies.source_type == movie_info['source_type']).first()

    if existing_movie:
        # if 88888888 not in existing_movie.production_companies:
        #     existing_movie.production_companies = movie_info["production_companies"] + [88888888]
        if "poster_path" in  movie_info:
            existing_movie.poster_path = movie_info["poster_path"]
        existing_movie.overview = movie_info["overview"]
        existing_movie.title = movie_info["title"]
        sess.commit()
        return dict(movie_id=existing_movie.id)
    # movie_data["production_companies"] = movie_info["production_companies"]+[88888888]

    movie = Movies(**movie_data)
    # sess.add(movie)
    sess.commit()

    return dict(movie_id=movie.id)


@gen.coroutine
@exc_handler
def insert_movie_info(movie_info, key_words_list, production_company_list, credits, **kwargs):
    """Query User Info."""
    sess = kwargs.get('sess')

    # movie info
    movie_data = {k: v for k, v in movie_info.items() if v is not None}
    movie = Movies(**movie_data)
    sess.add(movie)
    # sess.commit()

    # keywords
    key_words_list = [{"tmdb_id": d["id"], "name": d["name"], "movie_id": movie.id, "source_type":movie.source_type} for d in key_words_list]

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
