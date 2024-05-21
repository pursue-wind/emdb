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
    # stmt = insert(TVSeasons)
    # for tv_season in tv_seasons_list:
    #     stmt = stmt.values(**tv_season).on_conflict_do_nothing()
    #     sess.execute(stmt)
    # sess.commit()

    return dict()
@gen.coroutine
@exc_handler
def update_tv_seasons(tv_seasons_list, **kwargs):
    sess = kwargs.get('sess')
    for episode_data in tv_seasons_list:
        tmdb_series_id = episode_data.get('tmdb_series_id')
        tmdb_season_id = episode_data.get('tmdb_season_id')
        existing_season = sess.query(TVSeasons).filter(
            TVSeasons.tmdb_series_id == tmdb_series_id,
            TVSeasons.tmdb_season_id == tmdb_season_id
        ).first()

        if existing_season:
            for key, value in episode_data.items():
                setattr(existing_season, key, value)

    sess.commit()
    return dict()


@gen.coroutine
@exc_handler
def get_tv_season_params(season_id, **kwargs):
    sess = kwargs.get('sess')

    query = sess.query(TVSeasons).filter(TVSeasons.tmdb_season_id == season_id).first()
    if query:
        return dict(query.to_dict())
    else:
        return dict(air_date=None)
