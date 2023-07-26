from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import MoviesTranslations
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def query_movie_translations(movie_id, **kwargs):
    sess = kwargs.get('sess')
    res = sess.query(MoviesTranslations).filter(MoviesTranslations.id == movie_id).first()
    if res:
        res = res.to_dict()
    return res


@gen.coroutine
@exc_handler
def insert_movie_translations(translation_list, **kwargs):
    sess = kwargs.get('sess')
    stmt = insert(MoviesTranslations).values(translation_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()
    return dict()
