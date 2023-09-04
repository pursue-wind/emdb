from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.enums.enums import ReleaseTypes, get_key_by_value
from db.pgsql.mysql_models import ReleaseDate
from db.pgsql.base import exc_handler

@gen.coroutine
@exc_handler
def query_movie_release_dates(movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(ReleaseDate).filter(ReleaseDate.id == movie_id).all()
    release_dates_list = []
    for res in results:
        res = res.to_dict()
        # res["type"] = get_key_by_value(ReleaseTypes, res.get("type", 1))
        res["release_date"] = res["release_date"].strftime('%Y-%m-%d %H:%M:%S')
        release_dates_list.append(res)
    return dict(release_date=release_dates_list)


@gen.coroutine
@exc_handler
def insert_movie_release_dates(release_dates, **kwargs):
    sess = kwargs.get('sess')
    stmt = insert(ReleaseDate).values(release_dates).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()
    return dict()






