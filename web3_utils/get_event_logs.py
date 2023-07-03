import web3
from tornado import gen
from web3 import Web3

from web3.middleware import geth_poa_middleware

class Web3Utils:

    def __init__(self, provider_url):
        self.provider_url = provider_url

    def get_provider(self):
        w3_provider = Web3(Web3.HTTPProvider(self.provider_url))
        w3_provider.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3_provider

    def to_checksum_address(self, address):
        w3 = self.get_provider()
        check_address = w3.to_checksum_address(address)
        return check_address

    # @staticmethod
    def get_abi_content(self, abi_file_path):
        with open(abi_file_path, "r") as f:
            abi_content = f.read()
        return abi_content

    def get_block_info(self, block_number):
        w3 = self.get_provider()
        block_info = w3.eth.get_block(block_number)
        return block_info

    # @gen.coroutine
    def get_current_block_height(self):
        w3 = self.get_provider()
        current_block = w3.eth.get_block('latest')
        height = current_block.number
        return height
    # @gen.coroutine
    def get_block_timestamp(self, block_number):
        w3 = self.get_provider()
        block = w3.eth.get_block(block_number)
        timestamp = block.timestamp
        return timestamp

    @gen.coroutine
    def get_contract_event_logs(self, contract_address, abi_content, event_name, from_block, to_block):
        w3 = self.get_provider()
        contractObj = w3.eth.contract(address=contract_address, abi=abi_content)
        if event_name == "Transfer":
            logs_entries = contractObj.events.Transfer.create_filter(fromBlock=from_block, toBlock=to_block)
        elif event_name == "Mint":
            logs_entries = contractObj.events.Mint.create_filter(fromBlock=from_block, toBlock=to_block)
        elif event_name == "TransferSingle":
            logs_entries = contractObj.events.TransferSingle.create_filter(fromBlock=from_block, toBlock=to_block)
        elif event_name == "TransferBatch":
            logs_entries = contractObj.events.TransferBatch.create_filter(fromBlock=from_block, toBlock=to_block)
        elif event_name == "Burn":
            logs_entries = contractObj.events.Burn.create_filter(fromBlock=from_block, toBlock=to_block)
        elif event_name == "Create1155RaribleUserProxy":
            logs_entries = contractObj.events.Create1155RaribleUserProxy.create_filter(fromBlock=from_block,
                                                                                       toBlock=to_block)

        else:
            raise TypeError("Unknow Event Types!")
        event_logs = logs_entries.get_all_entries()
        return event_logs

    def parse_value(self, val):
        # check for nested dict structures to iterate through
        if 'dict' in str(type(val)).lower():
            return self.to_dict(val)
        # convert 'HexBytes' type to 'str'
        elif 'HexBytes' in str(type(val)):
            return val.hex()
        else:
            return val

    def to_dict(self, dictToParse):
        # convert any 'AttributeDict' type found to 'dict'
        parsedDict = dict(dictToParse)
        for key, val in parsedDict.items():
            if 'list' in str(type(val)):
                parsedDict[key] = [self.parse_value(x) for x in val]
            else:
                parsedDict[key] = self.parse_value(val)
        return parsedDict
