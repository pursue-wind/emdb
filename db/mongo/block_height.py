# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class BlockHeight(MongoBase):
    """Record scaned block and current block height"""

    @gen.coroutine
    def query_scaned_block_height(self, event_name, network, contract_address):
        result = yield self.block_height.find_one({"eventName": event_name, "network": network, "contractAddress": contract_address})
        return result

    @gen.coroutine
    def update_block_height(self, filter_params, scaned_block_height):
        yield self.block_height.update_one(filter_params, {'$set': scaned_block_height}, upsert=True)

    @gen.coroutine
    def insert_block_height(self, logs):
        yield self.block_height.insert(logs)



