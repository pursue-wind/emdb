import json
import traceback
from _decimal import Decimal
from datetime import datetime
from functools import wraps

from sqlalchemy import exc
from tornado.log import app_log

from lib.logger import dump_error

import enum

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config.config import CFG as cfg

print(cfg.pgsql)

DB_ENGINE = create_engine(
    cfg.pgsql,
    echo=False,
    pool_recycle=100,
    isolation_level='REPEATABLE_READ')

Session = scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=DB_ENGINE))
Base = declarative_base()
Base.query = Session.query_property()


def to_dict(self, *options, **alias):
    res = dict()
    for key in options:
        alias[key] = None

    for key in self.__dict__:
        if not alias or key in alias:
            if not key.startswith('_'):
                if isinstance(alias.get(key), str):
                    real_key = alias[key]
                else:
                    real_key = key
                if isinstance(self.__dict__[key], enum.Enum):
                    res[real_key] = self.__dict__[key].name
                else:
                    res[real_key] = self.__dict__[key]

    return res


Base.to_dict = to_dict


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
            # print(dir(exception))
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


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type '{}' is not JSON serializable".format(obj.__class__.__name__))
