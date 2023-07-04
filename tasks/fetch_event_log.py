import web3
from tornado.log import app_log

from . import mg
from tornado import ioloop, gen
import web3.constants

from web3_utils.get_event_logs import Web3Utils
from config import CFG as cfg
# from lib.utils.log_ext import logger

initial_block_height = cfg.scan_blocks.initial_height
scan_time_gap = cfg.scan_blocks.scan_time_gap

NETWORK = {
    "eth": "eth",
    "polygon": "polygon"
}

ZERO_ADDRESS = web3.constants.ADDRESS_ZERO

@gen.coroutine
def record_user_nft_info(event_logs, network_name):
    """
    record user's nft tokenId and amount
    :param event_logs: "List of ArtributeDict"
    :param network_name: "eth", "polygon".
    :param w3_obj: Web3 Object
    :return:
    """
    if not isinstance(event_logs, list):
        raise TypeError("Unknow event_logs type!")
    if len(event_logs) == 0:
        return

    for logs in event_logs:
        user_info = dict()
        to_addr = logs.args['to']
        from_addr = logs.args['from']
        collection_addr = logs.address
        event = logs.event
        token_ids = list()
        amount_list = list()
        if event == "TransferBatch":
            token_ids = [str(i) for i in logs.args["ids"]]
            amount_list = logs.args.values
        else:
            token_ids.append(str(logs.args.id))
            amount_list.append(logs.args.value)
        user_info["user_addr"] = from_addr
        user_info["collection_addr"] = collection_addr
        for i in range(len(token_ids)):
            user_info[token_ids[i]] = amount_list[i]
            if from_addr != ZERO_ADDRESS:
                user_info_from = yield mg.query_user_info(from_addr, collection_addr, token_ids[i], network_name)
                if user_info_from:
                    _amount_from = user_info_from.get("amount", 0)
                    amount_from = _amount_from - amount_list[i]
                else:
                    amount_from = amount_list[i]
                yield mg.update_user_info(from_addr, collection_addr, token_ids[i], network_name,
                                               {"amount": amount_from})
            else:
                nft_collection = yield mg.query_nft_collection(collection_addr, token_ids[i])
                if nft_collection:
                    supply = nft_collection.get("supply", 0)
                    total_supply = supply + amount_list[i]
                    mint = nft_collection.get("mint", 0)
                    total_mint = mint + amount_list[i]
                else:
                    total_supply = amount_list[i]
                    total_mint = amount_list[i]
                yield mg.update_nft_collection(collection_addr, token_ids[i], network_name, {"supply": total_supply, "mint": total_mint})

            if to_addr != ZERO_ADDRESS:
                user_info_to = yield mg.query_user_info(to_addr, collection_addr, token_ids[i], network_name)
                if user_info_to:
                    _amount_to = user_info_to.get("amount", 0)
                    amount_to = _amount_to + amount_list[i]
                else:
                    amount_to = amount_list[i]
                yield mg.update_user_info(to_addr, collection_addr, token_ids[i], network_name, {"amount": amount_to})
            else:
                nft_collection = yield mg.query_nft_collection(collection_addr, token_ids[i])
                if nft_collection:
                    supply = nft_collection.get("supply", 0)
                    burn = nft_collection.get("burn", 0)
                    total_supply = supply - amount_list[i]
                    total_burn = burn + amount_list[i]
                else:
                    total_supply = amount_list[i]
                    total_burn = amount_list[i]
                yield mg.update_nft_collection(collection_addr, token_ids[i], network_name, {"supply": total_supply, "burn": total_burn})

@gen.coroutine
def record_event_logs(event_logs, network_name, w3_obj):
    """
    :param event_logs: "List of ArtributeDict"
    :param network_name: "eth", "polygon".
    :param w3_obj: Web3 Object
    :return:
    """
    if not isinstance(event_logs, list):
        # app_log.error(event_logs)
        raise TypeError("Unknow result type,there is an error with fetch_event_log!")
    if len(event_logs) == 0:
        return
    logs_list = list()
    nft_flow_log_list = list()
    for logs in event_logs:
        log_dict = w3_obj.to_dict(logs)
        # _token_id = log_dict["args"]["id"]
        log_dict["network"] = network_name
        #
        nft_flow_log = parse_transfer_event_logs(log_dict, network_name)

        if "ids" in log_dict["args"].keys():
            log_dict["args"]["ids"] = nft_flow_log["tokenId"]
        else:
            log_dict["args"]["id"] = nft_flow_log["tokenId"]
        # get timestamp from mongodb first
        timestamp = yield get_block_timestamp(w3_obj, logs.blockNumber, network_name)

        nft_flow_log["timestamp"] = timestamp
        log_dict["timestamp"] = timestamp
        logs_list.append(log_dict)
        nft_flow_log_list.append(nft_flow_log)
    if len(logs_list) > 0:
        yield mg.insert_logs(logs_list)
        yield mg.insert_nft_flow_logs(nft_flow_log_list)


@gen.coroutine
def get_block_timestamp(w3_obj, block_number, network_name):
    """
    Get block timestamp from db first. if none, get from chain.
    :param w3_obj:
    :param block_number:
    :param network_name:
    :return:
    """
    timestamp_obj = yield mg.query_block_timestamp(block_number, network_name)
    if not timestamp_obj:
        # get timestamp from chain second
        timestamp = w3_obj.get_block_timestamp(block_number)
        yield mg.update_block_timestamp(block_number, network_name, timestamp)
    else:
        timestamp = timestamp_obj.get("timestamp", None)
    return timestamp


@gen.coroutine
def get_event_logs(w3_obj, contract_info, network_name):
    """
    :param w3_obj: "Web3 Object"
    :param contract_info: "contract from config"
    :param network_name: "eth", "polygon"
    :return: None
    """
    current_block_info = w3_obj.get_block_info('latest')
    current_block_height = current_block_info.number
    current_block_timestamp = current_block_info.timestamp
    # record block timestamp
    yield mg.update_block_timestamp(current_block_height, network_name, current_block_timestamp)

    event_types = contract_info["event"]
    block_gap = cfg.scan_blocks.scan_block_gap
    app_log.info(f"event_types:{event_types}")
    contract_address = get_contract_address(contract_info, network_name)

    for event_name in event_types:
        scaned_block_height = yield mg.query_scaned_block_height(event_name, network_name, contract_address)
        if not scaned_block_height:
            from_block = contract_info["initial_height"][network_name]
        else:
            app_log.info(f"scaned_block_height:{scaned_block_height['scanedBlockHeight']}")
            from_block = scaned_block_height["scanedBlockHeight"] + 1
        end_block = int(from_block) + block_gap

        if from_block > current_block_height:
            return
        if from_block <= current_block_height < end_block:
            end_block = current_block_height
        if from_block == end_block:
            # yield gen.sleep(5)
            continue
        try:
            abi = w3_obj.get_abi_content(contract_info["abi_file"])

            app_log.info(f"contract_address:{contract_address},event_name:{event_name},from_block:{from_block}, "
                        f"to_block:{end_block}, current_block_height:{current_block_height}")

            event_logs = yield w3_obj.get_contract_event_logs(contract_address, abi, event_name, int(from_block),
                                                              int(end_block))

            if contract_info["is_proxy"]:
                logs_list = list()
                for logs in event_logs:
                    log_dict = w3_obj.to_dict(logs)
                    log_dict["network"] = network_name
                    logs_list.append(log_dict)
                    event_log = parse_create1155_event_logs(log_dict, network_name)

                    # get timestamp from mongodb first
                    timestamp = yield get_block_timestamp(w3_obj, logs.blockNumber, network_name)

                    if event_log is not None:
                        event_log["timestamp"] = timestamp
                        # print(f"Create1155RaribleUserProxy event_log:{event_log}")
                        yield mg.insert_one_nft_flow_log(event_log)
                    address_proxy = w3_obj.to_checksum_address(log_dict["args"]["proxy"])
                    address_proxy_abi = w3_obj.get_abi_content(cfg.likn_collection_contracts["proxy_abi_file"])
                    for _event_name in cfg.likn_collection_contracts["event"]:
                        create1155_proxy_event_logs = yield w3_obj.get_contract_event_logs(address_proxy,
                                                                                           address_proxy_abi,
                                                                                           _event_name,
                                                                                           int(from_block),
                                                                                           int(end_block))

                        # record initial block height of proxy contract adddress
                        yield mg.update_block_height(
                            {"eventName": _event_name, "network": network_name, "contractAddress": address_proxy},
                            {"scanedBlockHeight": end_block})

                        app_log.info(f"create1155_proxy_event_logs : {address_proxy, _event_name, from_block, end_block}")

                        yield record_event_logs(create1155_proxy_event_logs, network_name, w3_obj)
                        yield record_user_nft_info(create1155_proxy_event_logs, network_name)

                if len(logs_list) > 0:
                    yield mg.insert_logs(logs_list)
            else:
                yield record_event_logs(event_logs, network_name, w3_obj)
                yield record_user_nft_info(event_logs, network_name)
            yield mg.update_block_height({"eventName": event_name, "network": network_name, "contractAddress": contract_address},
                                         {"scanedBlockHeight": end_block})

        except Exception as e:
            app_log.error(e)
            app_log.error(e.args)
            # if isinstance(e.args[0], dict) and str(e.args[0]["code"]) == "-32005":
            #     if block_gap < 1:
            #         return
            #     block_gap /= 2
            #     block_gap = int(block_gap)
            #     # end_block = from_block + block_gap
            #     yield time.sleep(0.5)


@gen.coroutine
def fetch_event_log():
    eth_provider_url = cfg.web3_provider.infura.eth
    polygon_provider_url = cfg.web3_provider.alchemy.polygon

    eht_provider = Web3Utils(eth_provider_url)
    polygon_provider = Web3Utils(polygon_provider_url)

    contracts = cfg.convert(cfg.contracts)

    while True:
        try:
            # 扫描配置文件合约地址事件
            for contract_info in contracts.values():
                yield [get_event_logs(eht_provider, contract_info, NETWORK.get("eth")),
                       get_event_logs(polygon_provider, contract_info, NETWORK.get("polygon"))]

            # 扫描动态创建的合约地址事件
            likn_collection_contracts = yield mg.query_proxy_address()
            app_log.info(likn_collection_contracts)
            for likn_contract in likn_collection_contracts:
                _likn_c = dict()
                _address = dict()
                _likn_c["event"] = cfg.likn_collection_contracts.event
                _likn_c["abi_file"] = cfg.likn_collection_contracts.proxy_abi_file
                _address[likn_contract["network"]] = likn_contract["proxy"]
                _likn_c["is_proxy"] = False
                _likn_c["address"] = _address
                if likn_contract["network"] == "eth":
                    _provider = eht_provider
                elif likn_contract["network"] == "polygon":
                    _provider = polygon_provider
                else:
                    raise TypeError("Unknow network!")
                yield get_event_logs(_provider, _likn_c, likn_contract["network"])
        except Exception as e:
            app_log.error(e)
            app_log.error(e.args)
            break
        yield gen.sleep(scan_time_gap)  # second


def parse_transfer_event_logs(event_logs, network_name):
    if not isinstance(event_logs, dict):
        return None
    flow_log = dict()
    event_name = event_logs["event"]
    flow_log["event"] = event_name
    flow_log["network"] = network_name
    flow_log["contractAddress"] = event_logs["address"]
    if event_name == "TransferBatch":
        _ids = event_logs["args"]["ids"]
        flow_log["tokenId"] = [str(_id) for _id in _ids]
        flow_log["amount"] = event_logs["args"]["values"]
    elif event_name == "TransferSingle":
        flow_log["tokenId"] = str(event_logs["args"]["id"])
        flow_log["amount"] = event_logs["args"]["value"]
    else:
        raise TypeError(f"Unknow event type!==> event: {event_name}")
    flow_log["from"] = event_logs["args"]["from"]
    flow_log["to"] = event_logs["args"]["to"]
    flow_log["transactionHash"] = event_logs["transactionHash"]
    flow_log["blockNumber"] = event_logs["blockNumber"]
    if "operator" in event_logs["args"].keys():
        flow_log["operator"] = event_logs["args"]["operator"]
    return flow_log


def parse_create1155_event_logs(event_logs, network_name):
    if not isinstance(event_logs, dict):
        return None
    event_log = dict()
    event_log["contractAddress"] = event_logs["address"]
    event_log["proxy"] = event_logs["args"]["proxy"]
    event_log["transactionHash"] = event_logs["transactionHash"]
    event_log["blockNumber"] = event_logs["blockNumber"]
    event_log["event"] = event_logs["event"]
    event_log["network"] = network_name
    return event_log


def get_contract_address(contract, network):
    """get a contract address from config"""
    if network == "eth":
        contract_address = contract["address"]["eth"]
    elif network == "polygon":
        contract_address = contract["address"]["polygon"]
    else:
        raise TypeError("Unspported Network Name!")
    contract_address = web3.Web3.to_checksum_address(contract_address)
    return contract_address
