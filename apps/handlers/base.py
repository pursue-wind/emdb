import base64
import contextvars
import json
import re

from objtyping import to_primitive
from sqlalchemy.ext.asyncio import AsyncSession
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

    def set_default_headers(self):
        origin_url = self.request.headers.get('Origin')
        if origin_url:
            self.set_header("Access-Control-Allow-Origin", origin_url)
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', '*')
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")

    async def options(self):
        self.set_status(200)
        await self.finish()

    async def get_session(self) -> AsyncSession:
        return self.session_factory()

    def success(self, data=None):
        if data:
            self.write({"code": 0, "msg": "success", "data": data})
            return
        self.write({"code": 0, "msg": "success"})

    def fail(self, status, msg):
        self.set_header('Content-Type', 'application/json')
        self.set_header('Access-Control-Allow-Origin', '*')
        self.write({"code": status, "msg": msg})

    def parse_form(self, *keys, required: list[str] = None, require_all: bool = False, valid_func=None):
        """Parse FORM argument like `get_argument`."""
        if require_all:
            required = keys

        if required and any(miss_arg := list(filter(lambda r: not self.get_argument(r, None), required))):
            raise MissingArgumentError(f': {miss_arg}')

        if valid_func and valid_func():
            raise MissingArgumentError('')

        res = list(map(lambda k: self.get_argument(k, None), keys))

        return res[0] if len(res) == 1 else res

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
