from sqlalchemy.dialects.postgresql import insert
from tornado import gen
from db.pgsql.mysql_models import TVEpisodes
from db.pgsql import exc_handler


@gen.coroutine
@exc_handler
def insert_tv_episodes(tv_episodes_detail, **kwargs):

    sess = kwargs.get('sess')
    tv_episodes_info = {k: v for k, v in tv_episodes_detail.items() if v is not None}
    tv_episodes = TVEpisodes(**tv_episodes_info)
    sess.add(tv_episodes)
    sess.commit()

    return dict(tv_episodes_id=tv_episodes.id)


@gen.coroutine
@exc_handler
def insert_tv_episodes_list(tv_episodes_list, **kwargs):

    sess = kwargs.get('sess')
    stmt = insert(TVEpisodes).values(tv_episodes_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()

    return dict()
