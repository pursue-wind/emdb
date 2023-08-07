# coding:utf-8
"""Base module for other views' modules."""
import base64
import json
import re
import time
import math
from urllib import parse
import traceback

from tornado import gen, httpclient
from tornado.log import app_log, gen_log
from tornado.web import Finish, MissingArgumentError, RequestHandler, HTTPError

from config import CFG as cfg
from config.status import NS
from lib.arguments import Arguments
from lib.errors import ParseJSONError
from lib.logger import dump_error, dump_out


ENFORCED = True
OPTIONAL = False

OPERATORS = {
    '$eq': lambda x, y: x == y,
    '$lt': lambda x, y: x < y,
    '$gt': lambda x, y: x > y,
    '$lte': lambda x, y: x <= y,
    '$gte': lambda x, y: x >= y,
    '$neq': lambda x, y: x != y,
}

AUTH_INFO = {"2gqcvdlkqbrm56": "feed0f24e31a235gd8b7e4bed1fec4dd2655"}

token_list = ['DJy87FAUwpIYn4KC188f099b152']

base64_pattern = re.compile(r'^[0-9a-zA-Z+/]+=*$')


class BaseHandler(RequestHandler):
    """Custom handler for other views module."""

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.params = None
        self.lang = None

    def _request_summary(self):
        s = ' '
        return f'{self.request.method.rjust(6, s)} {self.request.remote_ip.rjust(15, s)}  {self.request.path} '


    def log_exception(self, typ, value, tb):
        """Override to customize logging of uncaught exceptions.

        By default logs instances of `HTTPError` as warnings without
        stack traces (on the ``tornado.general`` logger), and all
        other exceptions as errors with stack traces (on the
        ``tornado.application`` logger).

        .. versionadded:: 3.1
        """
        if isinstance(value, HTTPError):
            if value.log_message:
                format = "%d %s: " + value.log_message
                args = ([value.status_code,
                         self._request_summary()] + list(value.args))
                gen_log.warning(format, *args)
                # gen_log.warning('\033[0;31m' + value.log_message + '\033[0m')
        else:
            app_log.error(
                "Uncaught exception %s\n%r",
                self._request_summary(),
                self.request,
                exc_info=(typ, value, tb))

    @gen.coroutine
    def options(self, *_args, **_kwargs):
        self.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, authorization')

        self.success()

    def fail(self, status, data=None, polyfill=None, msg=None, **_kwargs):
        """assemble and return error data."""

        if status != -1:
            msg = NS.get_status_message(status)
            # msg = "Unknow Error!"
        if data is None:
            data = dict()

        self.finish_with_json(
            dict(code=status, msg=msg, data=data or dict(), **_kwargs))

    def success(self, msg='Successfully.', data=None, **_kwargs):
        """assemble and return error data."""
        if data is None:
            data = dict()

        self.finish_with_json(dict(code=0, msg=msg, data=data))

    @gen.coroutine
    def fetch(self,
              api,
              method='GET',
              body=None,
              headers=None,
              schema='http',
              **_kwargs):
        """Fetch Info from backend."""
        body = body or dict()

        _headers = dict(host=self.request.host)
        if headers:
            _headers.update(headers)

        if '://' not in api:
            api = f'{schema}://{cfg.server.host}{api}'

        back_info = yield httpclient.AsyncHTTPClient().fetch(
            api,
            method=method,
            headers=_headers,
            body=json.dumps(body),
            raise_error=False,
            allow_nonstandard_methods=True)

        res_body = back_info.body and back_info.body.decode() or None

        if back_info.code >= 400:
            return Arguments(
                dict(http_code=back_info.code, res_body=res_body, api=api))

        try:
            return Arguments(json.loads(res_body))
        except json.JSONDecodeError:
            pass

    @gen.coroutine
    def check_auth(self, **kwargs):
        """Check auth."""
        headers = self.request.headers
        auth_header = headers.get("Authorization", None)
        try:
            auth_mode, auth_base64 = auth_header.split(' ', 1)
            auth_info = base64.b64decode(auth_base64)
            app_id, app_key = auth_info.decode('utf-8').split(":")
            if AUTH_INFO[app_id] != app_key:
                self.fail(401)
        except Exception as e:
            app_log.error(e)
            self.fail(401)

    def parse_form_arguments(self, *enforced_keys, **optional_keys):
        """Parse FORM argument like `get_argument`."""

        req = dict()
        for key in enforced_keys:
            req[key] = self.get_argument(key)
        for key in optional_keys:
            value_type = type(key)
            values = self.get_arguments(key)
            if len(values) == 0:
                req[key] = optional_keys.get(key)
            elif len(values) == 1:
                req[key] = value_type(values[0])
            else:
                req[key] = [value_type(v) for v in values]

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    def parse_json_arguments(self, *enforced_keys, **optional_keys):
        """Parse JSON argument like `get_argument`."""

        request_body = self.request.body

        if not request_body:
            request_body = b'{}'
        elif re.match(base64_pattern, request_body.decode()):
            request_body = base64.b64decode(request_body)

        try:
            req = json.loads(request_body.decode())
            app_log.info(f"request_body:{json.loads(request_body.decode())}")

        except json.JSONDecodeError as exception:
            dump_error('Exception:\n', request_body.decode())
            raise ParseJSONError(exception.doc)

        if not isinstance(req, dict):
            dump_error('Exception:\n', request_body.decode())
            raise ParseJSONError('Request should be a object.')

        for key in enforced_keys:
            if key not in req:
                dump_error('Exception:', request_body.decode())
                raise MissingArgumentError(f"'{key}'")

        for key in optional_keys:
            if key not in req:
                req[key] = optional_keys[key]

        req['remote_ip'] = self.request.remote_ip
        req['request_time'] = int(time.time())

        return Arguments(req)

    @gen.coroutine
    def prepare(self, *_args, **_kwargs):
        pass
        # if cfg.debug:
        #     info_list = [f'Input: {self.request.method} {self.request.path}']
        #     if self.request.query:
        #         query_list = [
        #             f'{i[0]:15s} {i[1]}'
        #             for i in parse.parse_qsl(self.request.query)
        #         ]
        #         info_list.append('\n' + '\n'.join(query_list))
        #     if self.request.body:
        #         info_list.append('\n' + self.request.body.decode())
        #     dump_in(*info_list)

    def finish_with_json(self, data):
        """Turn data to JSON format before finish."""
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')

        if cfg.debug:
            if self.request.method == 'POST':
                info_list = [
                    f'\033[0mOutput: {self.request.method} {self.request.path}'
                ]
                if self.request.query:
                    query_list = [
                        f'\033[0;32m{i[0]:15s} {i[1]}'
                        for i in parse.parse_qsl(self.request.query)
                    ]
                    info_list.append('\n' + '\n'.join(query_list))
                if self.request.body:
                    info_list.append('\n\033[0;32m' +
                                     self.request.body.decode())
                if data:
                    info_list.append('\n\033[0;33m' + json.dumps(data))
                dump_out(*info_list)
            # app_log.error(f"finish_with_json:{data}")
        raise Finish(json.dumps(data).encode())

    def write_error(self, status_code, **kwargs):
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
            self.finish(
                json.dumps(
                    dict(code=status_code, msg=self._reason,
                         data={})).encode())
        else:
            self.finish(
                json.dumps(
                    dict(code=status_code, msg=self._reason,
                         data={})).encode())

    def finish_with_bytes(self, data, content_type='text/plain'):
        """Turn data to JSON format before finish."""
        self.set_header('Access-Control-Allow-Origin', '*')

        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, bytes):
            pass
        else:
            data = str(data).encode()

        raise Finish(data)

    @gen.coroutine
    def wait(self, func, worker_mode=True, args=None, kwargs=None, **kw):
        """Method to waiting celery result."""
        if not args:
            args = list()
        if not kwargs:
            kwargs = dict()
        if worker_mode:
            async_task = func.apply_async(
                args=args, kwargs=dict(kwargs), **kw)
            while True:
                if async_task.status in ['PENDING', 'PROGRESS']:
                    yield gen.sleep(cfg.celery.sleep_time)
                elif async_task.status in ['SUCCESS', 'FAILURE']:
                    break
                else:
                    print('\n\nUnknown status:\n', async_task.status, '\n\n\n')
                    break

            if async_task.status != 'SUCCESS':
                dump_error(f'Task Failed: {func.name}[{async_task.task_id}]',
                           f'{str(async_task.result)}')
                result = dict(status=1, data=async_task.result)
                app_log.error(f"async_task result:{result}")
            else:
                result = async_task.result
                # app_log.error(f"async_task result:{result}")
            if result.get('status'):
                if result['status'] < 1000:
                    result['status'] = 3000 + result['status']
                dump_error(str(result))
                self.fail(**result)
            else:
                return result
        else:
            return func(*args, **kwargs)

    def send_task(self, func, worker_mode=True, args=None, kwargs=None, **kw):
        if not args:
            args = list()
        if not kwargs:
            kwargs = dict()
        meta = dict()

        func.apply_async(
            args=args, kwargs=dict(kwargs, meta=meta), **kw)

        return
