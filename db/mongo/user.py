# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class User(MongoBase):
    """Record scaned block and current block height"""

    @gen.coroutine
    def query_user_info(self, user_addr, collection_addr, token_id, network):
        result = yield self.user.find_one({"network": network, "token_id": token_id, "user_addr": user_addr,
                                           "collection_addr": collection_addr})
        return result

    @gen.coroutine
    def update_user_info(self, user_addr, collection_addr, token_id, network, user_info):
        filter_params = dict(
            network=network,
            tokenId=token_id,
            userAddr=user_addr,
            collectionAddr=collection_addr
        )
        yield self.user.update_one(filter_params, {'$set': user_info}, upsert=True)

    @gen.coroutine
    def query_user_nft_collections(self, user_addr, network):
        result = self.user.find({"userAddr": user_addr, "network": network}, projection=dict(_id=0))
        result_list = yield result.to_list(length=None)
        return result_list




