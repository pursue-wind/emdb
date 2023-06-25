
from . import mg
from tornado import ioloop, gen

from web3_utils.get_event_logs import Web3Utils
from config import CFG as cfg
from lib.utils.log_ext import logger

initial_block_height = cfg.scan_blocks.initial_height
scan_time_gap = cfg.scan_blocks.scan_time_gap


network = {
    "eth": "eth",
    "polygon": "polygon"
}


@gen.coroutine
def record_event_logs(event_logs, network_name, w3_obj):
    """
    :param event_logs: "List of ArtributeDict"
    :param network_name: "eth", "polygon".
    :param w3_obj: Web3 Object
    :return:
    """
    if isinstance(event_logs, list):
        if len(event_logs) == 0:
            return
        logs_list = list()
        for logs in event_logs:
            log_dict = w3_obj.to_dict(logs)
            _token_id = log_dict["args"]["id"]
            log_dict["network"] = network_name
            log_dict["args"]["id"] = str(_token_id)
            logs_list.append(log_dict)
            nft_flow_log = parse_transfer_event_logs(log_dict, network_name)
            if nft_flow_log is not None:
                yield mg.update_nft_flow_logs(nft_flow_log)
        if len(logs_list) > 0:
            yield mg.insert_logs(logs_list)
    else:
        logger.error(event_logs)
        raise TypeError("Unknow result type,there is an error with fetch_event_log!")

@gen.coroutine
def get_transfer_logs(w3_obj, contract_info, network_name):
    """
    :param w3_obj: "Web3 Object"
    :param contract_info: "contract from config"
    :param network_name: "eth", "polygon"
    :return: None
    """

    current_block_height = w3_obj.get_current_block_height()
    # contracts = cfg.convert(cfg.contracts)
    event_types = contract_info["event"]
    block_gap = 1000
    print(f"event_types:{event_types}")
    for event_name in event_types:
        scaned_block_height = yield mg.query_scaned_block_height(event_name, network_name)
        if not scaned_block_height:
            from_block = cfg.scan_blocks.initial_height[network_name]
        else:
            print(f"scaned_block_height:{scaned_block_height['scanedBlockHeight']}")
            from_block = scaned_block_height["scanedBlockHeight"] + 1
        end_block = int(from_block) + block_gap

        if from_block > current_block_height:
            return
        if from_block <= current_block_height < end_block:
            end_block = current_block_height
        if from_block == end_block:
            yield gen.sleep(12)
        logger.info(
            f"event_name:{event_name},from_block:{from_block}, to_block:{end_block}, current_block_height:{current_block_height}")
        # app_log.info(f"event_name:{event_name},from_block:{from_block}, to_block:{end_block}, current_block_height:{current_block_height}")
        try:
            abi = w3_obj.get_abi_content(contract_info["abi_file"])
            contract_address = w3_obj.checksum_address(get_contract_address(contract_info, network_name))
            logger.info(
                f"contract_address:{contract_address},event_name:{event_name},from_block:{from_block}, to_block:{end_block}, current_block_height:{current_block_height}")
            event_logs = yield w3_obj.get_contract_event_logs(contract_address, abi, event_name, int(from_block), int(end_block))
            # print(f"length of result:{len(event_logs)}, result:{event_logs}")
            # print(f"length of result:{len(event_logs)}")
            if contract_info["is_proxy"] is True:
                logs_list = list()
                for logs in event_logs:
                    log_dict = w3_obj.to_dict(logs)
                    log_dict["network"] = network_name
                    logs_list.append(log_dict)
                    event_log = parse_create1155_event_logs(log_dict, network_name)
                    if event_log is not None:
                        yield mg.update_nft_flow_logs(event_log)

                    address_proxy = w3_obj.checksum_address(log_dict["args"]["proxy"])
                    address_proxy_abi = w3_obj.get_abi_content(contract_info["proxy_abi_file"])
                    for _event_name in contract_info["proxy_contract_event"]:
                        create1155_proxy_event_logs = yield w3_obj.get_contract_event_logs(address_proxy,
                                                                                       address_proxy_abi,
                                                                                       _event_name,
                                                                                       int(from_block),
                                                                                       int(end_block))
                        record_event_logs(create1155_proxy_event_logs, network_name, w3_obj)

                if len(logs_list) > 0:
                    yield mg.insert_logs(logs_list)
            else:
                record_event_logs(event_logs, network_name, w3_obj)
            yield mg.update_block_height({"eventName": event_name, "network": network_name}, {"scanedBlockHeight": end_block})
            # from_block = end_block + 1
            # end_block = from_block + block_gap
        except Exception as e:
            logger.error(e)
            logger.error(e.args)
            # if isinstance(e.args[0], dict) and str(e.args[0]["code"]) == "-32005":
            #     if block_gap < 1:
            #         return
            #     block_gap /= 2
            #     block_gap = int(block_gap)
            #     # end_block = from_block + block_gap
            #     time.sleep(0.5)



@gen.coroutine
def fetch_event_log():
    eth_provider_url = cfg.web3_provider.alchemy.eth
    polygon_provider_url = cfg.web3_provider.alchemy.polygon
    eht_provider = Web3Utils(eth_provider_url)
    polygon_provider = Web3Utils(polygon_provider_url)
    contracts = cfg.convert(cfg.contracts)
    while True:
        try:
            for contract_info in contracts.values():
                yield [get_transfer_logs(eht_provider, contract_info, network.get("eth")),
                       get_transfer_logs(polygon_provider, contract_info, network.get("polygon"))]

                # yield get_transfer_logs(eht_provider, contract_info, network.get("eth"))
                # yield get_transfer_logs(polygon_provider, contract_info, network.get("polygon"))
        except Exception as e:
            logger.error(e.args)
            break
        yield gen.sleep(scan_time_gap)  # second


def parse_transfer_event_logs(event_logs, network_name):
    if not isinstance(event_logs, dict):
        return None
    flow_log = dict()
    inner_dict = dict()
    flow_log["network"] = network_name
    flow_log["contractAddress"] = event_logs["address"]
    # flow_log["event"] = event_logs["event"]
    flow_log["tokenId"] = event_logs["args"]["id"]

    inner_dict["event"] = event_logs["event"]
    inner_dict["from"] = event_logs["args"]["from"]
    inner_dict["to"] = event_logs["args"]["to"]
    inner_dict["transactionHash"] = event_logs["transactionHash"]
    inner_dict["blockNumber"] = event_logs["blockNumber"]
    if "operator" in event_logs["args"].keys():
        inner_dict["operator"] = event_logs["args"]["operator"]
    flow_log["logs"] = inner_dict

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

    return contract_address


