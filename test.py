import datetime
import json
import random

import requests

url = "http://127.0.0.1:8090/index"
param = [
    {
        "args":
        {
            "from": "0x612dCAfA236688A1A31EDf8A642917Ee19473529",
            "to": "0x8252Df1d8b29057d1Afe3062bf5a64D503152BC8",
            "tokenId": 7969
        },
        "event": "Transfer",
        "logIndex": 279,
        "transactionIndex": 145,
        "transactionHash": "0x7eab3099c4ed9c13db0bd36401a81d45d89ab8fe854c858de5770203b80db1d3",
        "address": "0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a",
        "blockHash": "0x77c7525af280b5f894be43368d803d957993fbd84f62d595653989707913ec55",
        "blockNumber": 17464954
    },
    {
        "args":
        {
            "from": "0x3b7F246d8340DE4Fe0495Bfd243FBEa798503C7f",
            "to": "0x8252Df1d8b29057d1Afe3062bf5a64D503152BC8",
            "tokenId": 2000259
        },
        "event": "Transfer",
        "logIndex": 503,
        "transactionIndex": 316,
        "transactionHash": "0x2887b54c8aa01fc72bc0537f6b2a746ee6af47d8f911096024998c7bc6cc17b6",
        "address": "0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a",
        "blockHash": "0x0dcfe8cbed8dd0e27af28b5eccb9f7b60ea9d49ebd0b415c3965fe41d83e4593",
        "blockNumber": 17465034
    },
    {
        "args":
        {
            "from": "0xD94d142a9E84dCD088BF458B06DA0d20448B8611",
            "to": "0x4387b3Ca2a8C99fd51DA5E694c8f391C180B9960",
            "tokenId": 669
        },
        "event": "Transfer",
        "logIndex": 209,
        "transactionIndex": 132,
        "transactionHash": "0x2a1a1a66666fe94f65e4a916e614e235e6d80292a5c35373d498102cd1889aa1",
        "address": "0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a",
        "blockHash": "0x55004be33b11ea77888394d6b62f26c110ad66c7c39290745263b41a20672db4",
        "blockNumber": 17466678
    },
    {
        "args":
        {
            "from": "0x221320D34800760E06B206aCd01e626e463eB03E",
            "to": "0xB5DA9A455F931EadA43DE8e30F52dA0d668a1099",
            "tokenId": 9355
        },
        "event": "Transfer",
        "logIndex": 276,
        "transactionIndex": 88,
        "transactionHash": "0x8df8e6b02073b2bc2b25fe06f2d73719989eb3f63402a3d0f9d5fd5a188853dd",
        "address": "0x059EDD72Cd353dF5106D2B9cC5ab83a52287aC3a",
        "blockHash": "0x421c2b28e979ce0e5b1b2f7b343f9e57a6c176f7a8f75b0b4e444955fe9829cf",
        "blockNumber": 17466721
    }
]

start = datetime.datetime.now()
for i in range(10):
    item = param[random.randrange(3)]
    # print(item)
    params = dict()
    params["log"] = item
    params["i"] = i
    try:
        res = requests.post(url, data=json.dumps(params))
    except Exception as e:
        print(e)
        continue

    # print(res.status_code)
end = datetime.datetime.now()
spend = end-start
print(f"总共花费时间：{spend}")