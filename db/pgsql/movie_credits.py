from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.base import exc_handler
from db.pgsql.mysql_models import MoviesCredits


@gen.coroutine
@exc_handler
def query_movie_credits(id, **kwargs):
    sess = kwargs.get('sess')
    res = sess.query(MoviesCredits).filter(MoviesCredits.id == id).first()
    if res:
        res = res.to_dict()
    return res


@gen.coroutine
@exc_handler
def query_movie_credit_by_tmdb_id(tmdb_id, **kwargs):
    sess = kwargs.get('sess')
    res = sess.query(MoviesCredits).filter(MoviesCredits.tmdb_id == tmdb_id).first()
    if res:
        emdb_credit_id = res.id
        return dict(id=emdb_credit_id)
    else:
        return dict()


@gen.coroutine
@exc_handler
def insert_movie_credits(credits_list, **kwargs):
    sess = kwargs.get('sess')
    stmt = insert(MoviesCredits).values(credits_list).on_conflict_do_nothing().returning(MoviesCredits.id,
                                                                                         MoviesCredits.tmdb_id)
    insert_rows = sess.execute(stmt).fetchall()
    sess.commit()

    inserted_ids = {row.tmdb_id: row.id for row in insert_rows}

    return inserted_ids
