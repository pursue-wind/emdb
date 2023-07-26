from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import MovieAlternativeTitles
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def query_alternative_title(**kwargs):
    sess = kwargs.get('sess')
    res = sess.query(MovieAlternativeTitles)
    movie_id = kwargs.get("movie_id")
    lang = kwargs.get("lang")
    if movie_id:
        res = res.filter(MovieAlternativeTitles.movie_id == movie_id)
    if lang:
        res = res.filter(MovieAlternativeTitles.iso_3166_1 == lang)

    title_list = list()
    for t in res.all():
        t = t.to_dict()
        title_list.append(t)
    return title_list


@gen.coroutine
@exc_handler
def insert_movie_alternative_titles(alternative_titles, **kwargs):
    sess = kwargs.get('sess')

    # stmt = insert(MovieAlternativeTitles).values(alternative_titles).on_conflict_do_nothing()

    stmt = insert(MovieAlternativeTitles).values(alternative_titles)
    do_update_stmt = stmt.on_conflict_do_update(
        index_elements=['movie_id', 'iso_3166_1', "title"],
        set_={
            'movie_id': stmt.excluded.movie_id,
            'iso_3166_1': stmt.excluded.iso_3166_1,
            'title': stmt.excluded.title,
        }
    )

    sess.execute(do_update_stmt)
    sess.commit()

    return dict()
