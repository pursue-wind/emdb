from sqlalchemy.dialects.postgresql import insert
from tornado import gen

from db.pgsql.enums.enums import CreditType
from db.pgsql.mysql_models import MoviesCredits, MovieCreditsRelation
from db.pgsql.base import exc_handler

@gen.coroutine
@exc_handler
def query_movie_credits_relation(id, **kwargs):
    sess = kwargs.get('sess')
    res = sess.query(MovieCreditsRelation).filter(MovieCreditsRelation.id == id).first()
    if res:
        res = res.to_dict()
    return res


@gen.coroutine
@exc_handler
def insert_batch_movie_credits_relation(relations, **kwargs):
    sess = kwargs.get('sess')

    stmt = insert(MovieCreditsRelation).values(relations).on_conflict_do_nothing()
    sess.execute(stmt)
    sess.commit()
    return dict()


@gen.coroutine
@exc_handler
def query_movie_credits_by_movie_id(movie_id, **kwargs):
    sess = kwargs.get('sess')

    movie_credits_relation = sess.query(MovieCreditsRelation).filter(MovieCreditsRelation.movie_id == movie_id).all()
    credits_list = dict()
    cast = []
    crew = []
    for relation in movie_credits_relation:
        credit_info = {}
        credit_detail = relation.credit
        credit_info["name"] = credit_detail.name
        credit_info["original_name"] = credit_detail.original_name
        credit_info["known_for_department"] = credit_detail.known_for_department
        credit_info["profile_path"] = credit_detail.profile_path
        credit_info["movie_id"] = relation.movie_id
        credit_info["order"] = relation.order
        credit_info["name"] = credit_detail.name
        credit_info["tmdb_id"] = credit_detail.tmdb_id
        credit_info["adult"] = credit_detail.adult
        credit_info["sex"] = credit_detail.gender

        if relation.type == CreditType.cast.value:
            credit_info["character"] = relation.character
            cast.append(credit_info)
        else:
            credit_info["department"] = relation.department
            credit_info["job"] = relation.job
            crew.append(credit_info)
    credits_list["cast"] = cast
    credits_list["crew"] = crew

    return credits_list















