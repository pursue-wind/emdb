# from handlers.test import IndexHandler
from handlers.event_log_handler import EventLogListHandler
from handlers.nft_collections_handler import UserNftCollectionsHandler, NftSupplyHandler
from handlers.collected_nft_handler import CollectedNftAmountHandler

INDEX_ROUTE = [
    # ("/index", IndexHandler),
    ("/nft/event_logs", EventLogListHandler),
    ("/nft/query_collected_nft", CollectedNftAmountHandler),

    ("/user/query_user_nft_collections", UserNftCollectionsHandler),

    ("/nft/query_nft_supply", NftSupplyHandler),

]