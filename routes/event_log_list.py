# from handlers.test import IndexHandler
from handlers.event_log_handler import EventLogListHandler

INDEX_ROUTE = [
    # ("/index", IndexHandler),
    ("/nft/event_logs", EventLogListHandler)
]