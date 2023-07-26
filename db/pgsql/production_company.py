from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.mysql_models import ProductionCompany
from db.pgsql.base import exc_handler


@gen.coroutine
@exc_handler
def batch_insert_production_company(production_company_list, **kwargs):
    sess = kwargs.get('sess')

    stmt = insert(ProductionCompany).values(production_company_list).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()

    return dict()


@gen.coroutine
@exc_handler
def query_company_by_name(company_name, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(ProductionCompany).filter(ProductionCompany.name.ilike(f"%{company_name}%")).all()
    company_list = [cp.to_dict() for cp in results]
    return dict(companies=company_list)


@gen.coroutine
@exc_handler
def query_company_by_ids(ids, **kwargs):
    sess = kwargs.get('sess')
    results = sess.query(ProductionCompany).filter(ProductionCompany.tmdb_id.in_(ids)).all()
    company_list = [cp.to_dict() for cp in results]
    return dict(companies=company_list)

