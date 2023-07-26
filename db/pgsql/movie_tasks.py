from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import FetchMovieTasks
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def query_movie_tasks(movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(FetchMovieTasks).filter(FetchMovieTasks.tmdb_movie_id == movie_id).first()
    if results:
        results = results.to_dict()
    return results


@gen.coroutine
@exc_handler
def update_movie_tasks(movie_id, info, **kwargs):
    sess = kwargs.get('sess')
    result = sess.query(FetchMovieTasks).filter(FetchMovieTasks.tmdb_movie_id==movie_id).update(info)
    sess.commit()
    return dict()
