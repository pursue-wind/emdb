# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class NftCollection(MongoBase):
    """Record scaned block and current block height"""

    @gen.coroutine
    def query_nft_collection(self, contract_address, token_id):
        result = yield self.nft_collections.find_one({"contractAddress": contract_address, "tokenId": token_id},
                                                     projection=dict(_id=0))
        return result

    @gen.coroutine
    def update_nft_collection(self, contract_address, token_id, network, update_info):
        yield self.nft_collections.update_one({"contractAddress": contract_address,
                                               "tokenId": token_id,
                                               "network": network},
                                              {'$set': update_info},
                                              upsert=True)
