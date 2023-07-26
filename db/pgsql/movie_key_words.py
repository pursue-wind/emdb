from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import MovieKeyWords
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def query_movie_keywords(movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(MovieKeyWords).filter(MovieKeyWords.movie_id == movie_id).all()
    keyword_lists = []
    for res in results:
        keyword_lists.append(res.name)
    return keyword_lists


@gen.coroutine
@exc_handler
def insert_movie_key_words(key_words_list, **kwargs):
    sess = kwargs.get('sess')

    stmt = insert(MovieKeyWords).values(key_words_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()

    return dict()
