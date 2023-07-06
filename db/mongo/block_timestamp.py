# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class BlockTimestamp(MongoBase):
    """Record scaned block and current block height"""
    @gen.coroutine
    def query_block_timestamp(self, block_number, network):
        result = yield self.block_timestamp.find_one({"blockNumber": block_number, "network": network})
        return result

    @gen.coroutine
    def update_block_timestamp(self, block_number, network, timestamp):
        info = dict(timestamp=timestamp)
        yield self.block_timestamp.update_one(dict(blockNumber=block_number, network=network), {'$set': info}, upsert=True)

    @gen.coroutine
    def insert_block_timestamp(self, block_number, network, timestamp):
        info = dict(
            blockNumber=block_number,
            network=network,
            timestamp=timestamp
        )
        yield self.block_timestamp.insert_one(info)

