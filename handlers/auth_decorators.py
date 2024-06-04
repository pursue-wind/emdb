import base64
import functools
import urllib
from typing import Optional, Awaitable, Callable
from urllib.parse import urlencode

from tornado import gen
from tornado.web import RequestHandler, HTTPError

from handlers.base_handler import BaseHandler

AUTH_INFO = {
    "2gqcvdlkqbrm56": "feed0f24e31a235gd8b7e4bed1fec4dd2655",
    "2aqcldlkq1rm57": "feed0ff4e31g235gd8b7e4bed1fec4dd2651"
}


def authenticated_async(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get("Authorization", None)
        if auth_header:
            auth_mode, auth_base64 = auth_header.split(' ', 1)
            auth_info = base64.b64decode(auth_base64)
            app_id, app_key = auth_info.decode('utf-8').split(":")
            if app_id not in AUTH_INFO:
                self.fail(401)
            if AUTH_INFO[app_id] != app_key:
                self.fail(401)
            await func(self, *args, **kwargs)
        else:
            self.set_status(401)
        self.finish({})

    return wrapper


def auth(
        method: Callable[..., Optional[Awaitable[None]]]
) -> Callable[..., Optional[Awaitable[None]]]:
    """Decorate methods with this to require that the user be logged in.

    If the user is not logged in, they will be redirected to the configured
    `login url <RequestHandler.get_login_url>`.

    If you configure a login url with a query parameter, Tornado will
    assume you know what you're doing and use it as-is.  If not, it
    will add a `next` parameter so the login page knows where to send
    you once you're logged in.
    """

    @functools.wraps(method)
    def wrapper(self: BaseHandler, *args, **kwargs) -> Optional[Awaitable[None]]:
        auth_header = self.request.headers.get("Authorization", None)
        if auth_header:
            try:
                auth_mode, auth_base64 = auth_header.split(' ', 1)
                auth_info = base64.b64decode(auth_base64)
                app_id, app_key = auth_info.decode('utf-8').split(":")
                if app_id not in AUTH_INFO:
                    raise HTTPError(401)
                if AUTH_INFO[app_id] != app_key:
                    raise HTTPError(401)
            except Exception:
                raise HTTPError(401)
            return method(self, *args, **kwargs)
        raise HTTPError(401)

    return wrapper
