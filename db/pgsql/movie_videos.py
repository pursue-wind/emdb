from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import Videos
from db.pgsql.base import exc_handler

@gen.coroutine
@exc_handler
def query_movie_videos(movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(Videos).filter(Videos.movie_id == movie_id).all()
    videos_list = []
    for video in results:
        video = video.to_dict()
        video["published_at"] = video["published_at"].strftime('%Y-%m-%d %H:%M:%S')
        videos_list.append(video)
    return dict(videos=videos_list)


@gen.coroutine
@exc_handler
def insert_movie_videos(videos_list, **kwargs):
    sess = kwargs.get('sess')
    stmt = insert(Videos).values(videos_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()
    return dict()
