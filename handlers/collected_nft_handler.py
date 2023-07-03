import json

import web3.constants
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler
from tasks.fetch_event_log import ZERO_ADDRESS

class CollectedNftAmountHandler(BaseHandler):
    """Collected nft amount"""

    @gen.coroutine
    def post(self):
        args = self.parse_json_arguments('owner_address', 'contract_address', 'token_id')
        owner_address = args.owner_address
        contract_addr = args.contract_address
        token_id = args.token_id
        yield self.check_auth()
        if not web3.Web3.is_address(contract_addr) or not web3.Web3.is_address(owner_address):
            self.fail(400)

        result = yield self.mg.query_collected_nft(owner_address, contract_addr, token_id)
        collected_cnt = 0
        for re in result:
            if re["to"] != ZERO_ADDRESS:
                collected_cnt += re["amount"]
        self.success(data=dict(ownerAddress=owner_address, contractAddr=contract_addr,
                               tokenId=token_id, collectedCnt=collected_cnt))
