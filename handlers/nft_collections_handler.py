import json

import web3.constants
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler


class NftCollectionsHandler(BaseHandler):
    """User's nft collection"""

    @gen.coroutine
    def post(self):
        args = self.parse_json_arguments('contract_address', 'token_id')
        contract_addr = args.contract_address
        token_id = args.token_id
        yield self.check_auth()
        if not web3.Web3.is_address(contract_addr):
            self.fail(400)
        result = yield self.mg.query_nft_collection(contract_addr, token_id)
        self.success(data=result)
