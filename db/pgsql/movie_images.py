from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.enums.enums import get_key_by_value
from db.pgsql.mysql_models import Imgs
from db.pgsql.base import exc_handler

@gen.coroutine
@exc_handler
def query_movie_images(movie_id, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(Imgs).filter(Imgs.movie_id == movie_id).all()
    images_list = []
    for image in results:
        image = image.to_dict()
        images_list.append(image)
    return dict(images=images_list)


@gen.coroutine
@exc_handler
def insert_movie_images(images_list, **kwargs):
    sess = kwargs.get('sess')

    stmt = insert(Imgs).values(images_list).on_conflict_do_nothing()
    # stmt = insert(Imgs).values(images_list)
    # do_update_stmt = stmt.on_conflict_do_update(
    #     index_elements=['movie_id', 'iso_639_1', 'url'],
    #     set_={
    #         'movie_id': stmt.excluded.movie_id,
    #         'iso_639_1': stmt.excluded.iso_639_1,
    #         'url': stmt.excluded.url,
    #         'type': stmt.excluded.type
    #     }
    # )
    # todo 使用on_conflict_do_update时插入重复的数据依然有部分成功，自增id会跳跃

    sess.execute(stmt)
    sess.commit()


    return dict()
