import json

import web3.constants
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler


class UserNftCollectionsHandler(BaseHandler):
    """User's nft collections"""

    @gen.coroutine
    def post(self):
        args = self.parse_json_arguments('user_address', 'network')
        user_address = args.user_address
        network = args.network
        yield self.check_auth()
        if not web3.Web3.is_address(user_address):
            self.fail(400)
        result = yield self.mg.query_user_nft_collections(user_address, network)
        res_dict = dict()
        res_dict["userAddress"] = user_address
        res_dict["network"] = network
        collections = list()
        for res in result:
            del res["userAddr"]
            del res["network"]
            mint_res = yield self.mg.query_nft_flow_to_user(res["collectionAddr"], res["tokenId"],
                                                            network, user_address)
            print(mint_res)
            mint_amount = 0
            for _mint in mint_res:
                _amount = _mint["amount"]
                mint_amount += _amount
            res["amount"] = res["amount"] - mint_amount
            collections.append(res)
        res_dict["collections"] = collections
        self.success(data=res_dict)


class NftSupplyHandler(BaseHandler):
    """query supply of nft"""

    @gen.coroutine
    def post(self):
        args = self.parse_json_arguments('contract_address', 'token_id')
        contract_addr = args.contract_address
        token_id = args.token_id
        yield self.check_auth()
        if not web3.Web3.is_address(contract_addr):
            self.fail(400)
        result = yield self.mg.query_nft_collection(contract_addr, token_id)
        if result:
            self.success(data=dict(
                contractAddress=contract_addr,
                tokenId=token_id,
                supply=result.get("supply", 0),
                mint=result.get("mint", 0),
                burn=result.get("burn", 0)
            ))
        else:
            self.success(data=dict(
                contractAddress=contract_addr,
                tokenId=token_id,
                supply=0,
                mint=0,
                burn=0
            ))
