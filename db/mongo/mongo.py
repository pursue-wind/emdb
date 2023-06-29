# coding:utf-8
"""Predefination of mongo schema."""

from pymongo import MongoClient
from config import CFG as cfg
from db.mongo.block_height import BlockHeight
from db.mongo.event_logs import LogsTasks
from db.mongo.nft_flow_log import NftFlowLog

MS_CLIENT = MongoClient(cfg.mongo.client).__getattr__(cfg.mongo.db)


class Mongo(LogsTasks, BlockHeight, NftFlowLog):
    pass


def init_mongo():
    """init collection & index"""
    # MS_CLIENT.logs.drop_indexes()
    MS_CLIENT.logs.create_index('address')

    # MS_CLIENT.blockHeight.drop_indexes()
    MS_CLIENT.blockHeight.create_index('height')

    MS_CLIENT.account.drop_indexes()
    MS_CLIENT.account.create_index('user_address')

    MS_CLIENT.nftFlowLog.drop_indexes()
    MS_CLIENT.nftFlowLog.create_index([('network', 1), ('contractAddress', 1), ('tokenId', 1)])

    MS_CLIENT.collections.create_index('address')
    MS_CLIENT.user_logs.create_index('user_addr')






