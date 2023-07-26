import traceback
from functools import wraps

from sqlalchemy import exc
from tornado.log import app_log

from db.pgsql.base import Session
from lib.logger import dump_error


def exc_handler(function):
    """Wrap a handle shell to a query function."""

    @wraps(function)
    def wrapper(*args, **kwargs):
        """Function that wrapped."""
        session = Session()
        try:
            res = function(sess=session, *args, **kwargs)
        except exc.IntegrityError as exception:
            res = dict(
                status=1,
                msg=str(exception.orig),
                data=dict(
                    error=exception.__class__.__name__,
                    code=exception.code,
                    detail=exception.detail,
                    params=exception.params,
                    orig=str(exception.orig)))
            session.rollback()
            print(dir(exception))
        except exc.ProgrammingError as exception:
            res = dict(status=2, msg=str(exception.orig))
            app_log.error(f"Op dbs error!：{res},{exception}")
            session.rollback()
        except exc.OperationalError as exception:
            res = dict(status=3, msg=str(exception.orig))
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except exc.InternalError as exception:
            res = dict(
                status=4,
                msg=str(exception.orig),
                data=dict(
                    error=exception.__class__.__name__,
                    code=exception.code,
                    detail=exception.detail,
                    params=exception.params,
                    orig=str(exception.orig)))
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except exc.ResourceClosedError as exception:
            res = dict(status=11, msg=str(exception))
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except UnicodeEncodeError as exception:
            res = dict(status=12, msg=str(exception))
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except exc.InvalidRequestError as exception:
            res = dict(status=13, msg=str(exception))
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except exc.SQLAlchemyError as exception:
            res = dict(status=exception.args[0], msg=exception.args[1])
            app_log.error(f"Op dbs error!：{exception}")
            session.rollback()
        except Exception as e:
            dump_error('my exception\n', traceback.format_exc())
            app_log.error(f"Op dbs error!：{e}")
            session.rollback()
            res = dict(status=999, msg='Unknown Error.')
        finally:
            session.close()

        if res and 'status' in res:
            return res
        else:
            return dict(status=0, data=res)  # {"status": 0, "data": res}

    return wrapper