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


@gen.coroutine
@exc_handler
def get_tv_season_params(season_id, **kwargs):
    sess = kwargs.get('sess')

    query = sess.query(TVSeasons).filter(TVSeasons.tmdb_season_id == season_id).first()

    return dict(name=query.name,episode_count=query.episode_count
                ,external_ids=query.external_ids,season_number=query.season_number)
