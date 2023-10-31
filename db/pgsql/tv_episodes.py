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


@gen.coroutine
@exc_handler
def get_tv_episodes_list(tmdb_season_id, **kwargs):
    sess = kwargs.get('sess')
    result = sess.query(TVEpisodes).filter(TVEpisodes.tmdb_season_id == tmdb_season_id)
    total = result.count()
    episodes_list = result.all()
    episodes=[]
    for episode in episodes_list:
        episode = episode.to_dict()
        episodes.append(episode)
    return dict(episodes_list=episodes,total=total)
