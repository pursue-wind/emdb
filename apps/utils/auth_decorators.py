import base64
import functools
from typing import Optional, Awaitable, Callable
from collections import OrderedDict
from tornado.web import HTTPError

from apps.handlers.base import BaseHandler

AUTH_INFO = {
    "2gqcvdlkqbrm56": "feed0f24e31a235gd8b7e4bed1fec4dd2655",
    "2aqcldlkq1rm57": "feed0ff4e31g235gd8b7e4bed1fec4dd2651"
}


def auth(
        method: Callable[..., Optional[Awaitable[None]]]
) -> Callable[..., Optional[Awaitable[None]]]:
    """Decorate methods with this to check Authorization headers."""

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


def async_lru_cache(maxsize=128):
    def decorator(func):
        cache = OrderedDict()

        @functools.wraps(func)
        async def wrapper(*args):
            if args in cache:
                # Move the key to the end to show that it was recently used
                cache.move_to_end(args)
                print("======================")
                print("======================")
                return cache[args]

            result = await func(*args)
            cache[args] = result

            # Remove the first key-value pair if the cache is over the max size
            if len(cache) > maxsize:
                cache.popitem(last=False)

            return result

        return wrapper

    return decorator
