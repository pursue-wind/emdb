from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import MoviesTranslations
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def query_movie_translations(movie_id, **kwargs):
    sess = kwargs.get('sess')
    result = sess.query(MoviesTranslations).filter(MoviesTranslations.movie_id == movie_id).all()
    translations_list = []
    for res in result:
        res = res.to_dict()
        translations_list.append(res)
    return translations_list


@gen.coroutine
@exc_handler
def insert_movie_translations(translation_list, **kwargs):
    sess = kwargs.get('sess')
    stmt = insert(MoviesTranslations).values(translation_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()
    return dict()
