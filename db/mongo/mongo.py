# coding:utf-8
"""Predefination of mongo schema."""

from pymongo import MongoClient
from config import CFG as cfg
from db.mongo.block_height import BlockHeight
from db.mongo.block_timestamp import BlockTimestamp
from db.mongo.event_logs import LogsTasks
from db.mongo.nft_collections import NftCollection
from db.mongo.nft_flow_log import NftFlowLog
from db.mongo.user import User

MS_CLIENT = MongoClient(cfg.mongo.client).__getattr__(cfg.mongo.db)


class Mongo(LogsTasks, BlockHeight, NftFlowLog, User, BlockTimestamp, NftCollection):
    pass


def init_mongo():
    """init collection & index"""
    MS_CLIENT.logs.drop_indexes()
    MS_CLIENT.logs.create_index('transactionHash')

    MS_CLIENT.block_height.drop_indexes()
    MS_CLIENT.block_height.create_index([("contractAddress", 1), ("network", 1), ("eventName", 1)])

    MS_CLIENT.user.drop_indexes()
    MS_CLIENT.user.create_index([("network", 1), ("tokenId", 1), ("userAddr", 1), ("contractAddress", 1)])

    MS_CLIENT.nft_flow_log.drop_indexes()
    MS_CLIENT.nft_flow_log.create_index([('network', 1), ('contractAddress', 1), ('tokenId', 1)])

    MS_CLIENT.nft_collections.create_index([('contractAddress', 1), ('tokenId', 1)])

    # MS_CLIENT.user_logs.drop_indexes()
    # MS_CLIENT.user_logs.create_index('user_address')

    MS_CLIENT.block_timestamp.drop_indexes()
    MS_CLIENT.block_timestamp.create_index([('blockNumber', 1), ("network", 1)], unique=True)






