from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql import exc_handler
from db.pgsql.mysql_models import TVSeasons


@gen.coroutine
@exc_handler
def insert_tv_seasons(tv_seasons_list, **kwargs):

    sess = kwargs.get('sess')

    stmt = insert(TVSeasons).values(tv_seasons_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()

    return dict()
