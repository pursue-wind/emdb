import base64
import contextvars
import json
import re

from objtyping import to_primitive
from tornado.web import RequestHandler, MissingArgumentError

base64_pattern = re.compile(r'^[0-9a-zA-Z+/]+=*$')

# 定义一个全局的上下文变量
language_var = contextvars.ContextVar('language')


class BaseHandler(RequestHandler):
    def initialize(self, session_factory):
        self.session_factory = session_factory

    async def prepare(self):
        # 从请求参数中获取 `language` 参数并赋值给处理器实例
        self.language = self.get_argument('lang', 'en')
        language_var.set(self.language)

    async def options(self, *_args, **_kwargs):
        self.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, authorization')

    async def get_session(self):
        return self.session_factory()

    def success(self, data=None):
        if data:
            self.write({"code": 0, "msg": "success", "data": data})
            return
        self.write({"code": 0, "msg": "success"})

    def parse_form(self, *keys, required: list[str] = None, require_all: bool = False, valid_func=None):
        """Parse FORM argument like `get_argument`."""
        if require_all:
            required = keys

        if required and any(miss_arg := list(filter(lambda r: not self.get_argument(r, None), required))):
            raise MissingArgumentError(f': {miss_arg}')

        if valid_func and valid_func():
            raise MissingArgumentError('')

        return list(map(lambda k: self.get_argument(k, None), keys))

    def parse_body(self, *keys: str, required: list[str] = None, require_all: bool = False, valid_func=None) -> []:
        """Parse JSON argument like `get_argument`."""

        request_body = self.request.body

        if not request_body:
            request_body = b'{}'
        elif re.match(base64_pattern, request_body.decode()):
            request_body = base64.b64decode(request_body)

        try:
            req = json.loads(request_body.decode())
        except json.JSONDecodeError as exception:
            raise MissingArgumentError(exception.doc)

        if not isinstance(req, dict):
            raise MissingArgumentError('Request should be a object.')

        if require_all:
            required = keys

        if required and len(miss_arg := set(required) - req.keys()) > 0:
            raise MissingArgumentError(str(miss_arg))

        if valid_func and len(filter(valid_func(req), keys)) == 0:
            raise MissingArgumentError('Missing argument')

        return list(map(lambda k: req[k] if k in req.keys() else None, keys))

    @staticmethod
    def to_primitive(sqlalchemy_obj):
        return to_primitive(sqlalchemy_obj)
