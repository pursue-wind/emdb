from tornado import gen
from db.pgsql.base import exc_handler
from db.pgsql.mysql_models import Movies


@gen.coroutine
@exc_handler
def query_tv_by_company_id(tmdb_company_id, **kwargs):
    sess = kwargs.get('sess')
    page_num = kwargs.get('page_num')
    page_size = kwargs.get('page_size')
    tv_name = kwargs.get('tv_name')
    query = sess.query(Movies).filter(Movies.production_companies.any(tmdb_company_id))
    if tv_name:
        query = query.filter(Movies.original_title.ilike(f"%{tv_name}%"))

    total = query.count()

    offset = (int(page_num) - 1) * int(page_size)
    tv_list = query.offset(offset).limit(page_size).all()
    _tv_list = []
    for tv in tv_list:
        tv = tv.to_dict()
        _tv_list.append(tv)
    return dict(tvs=_tv_list, total=total, page_num=page_num, page_size=page_size)
