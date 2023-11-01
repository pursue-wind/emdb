from tornado import gen

from db.pgsql import exc_handler
from db.pgsql.mysql_models import TVSeriesAdditional
from sqlalchemy.dialects.postgresql import insert


@gen.coroutine
@exc_handler
def insert_tv_additional_info(tv_additional_info, **kwargs):
    sess = kwargs.get('sess')
    tv_additional_info = {k: v for k, v in tv_additional_info.items() if v is not None}
    stmt = insert(TVSeriesAdditional).values(tv_additional_info).on_conflict_do_nothing()
    # tv_series_additional = TVSeriesAdditional(**tv_additional_info)
    # sess.add(tv_series_additional)
    sess.execute(stmt)
    sess.commit()

    return dict()


@gen.coroutine
@exc_handler
def get_tv_additional_info(series_id, **kwargs):
    sess = kwargs.get('sess')
    result = sess.query(TVSeriesAdditional).filter(TVSeriesAdditional.tmdb_series_id == series_id).first()

    return dict(data=result.to_dict())
