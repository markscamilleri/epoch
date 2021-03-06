# coding: utf-8

"""
    Aeternity Epoch

    This is the [Aeternity](https://www.aeternity.com/) Epoch API.

    OpenAPI spec version: 1.0.0
    Contact: apiteam@aeternity.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import os
import sys
import unittest
import datetime

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.external_api import ExternalApi
from swagger_client.api_client import ApiClient
from swagger_client.models.block import Block
from swagger_client.models.signed_tx import SignedTx
from swagger_client.models.coinbase_tx import CoinbaseTx

def utc_now():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970,1,1)
    return int((d - epoch).total_seconds())

def signed_coinbase_tx(height):
    account = "BAAggMEhrC3ODBqlYeQ6dk00F87AKMkV6kkyhgfJ/luOzGUC+4APxFkVgAYPai3TjSyLRObv0GeDACg1ZxwnfHY="
    coinbase = CoinbaseTx(pubkey = account, nonce = height - 1)
    return SignedTx(data = coinbase, type = "coinbase",
            signatures =
            ["Some signature"])


class TestExternalApi(unittest.TestCase):
    EXT_API = {
        'dev1': ExternalApi(ApiClient(host='localhost:3013/v1')),
        'dev2': ExternalApi(ApiClient(host='localhost:3023/v1')),
        'dev3': ExternalApi(ApiClient(host='localhost:3033/v1')),
    }
    """ ExternalApi unit test stubs """

    def test_get_top(self):
        """
        Test case for get_top

        
        """
        api = self.EXT_API['dev1']
        top = api.get_top()

    def test_get_block_by_height(self):
        """
        Test case for get_block_by_height

        
        """
        api = self.EXT_API['dev1']
        block = api.get_block_by_height(0)

    def test_get_block_by_hash(self):
        """
        Test case for get_block_by_hash (last block)

        
        """
        api = self.EXT_API['dev1']
        top = api.get_top()
        block = api.get_block_by_hash(top.hash)

    def test_get_account_balance(self):
        """
        Test case for get_account_balance (account not present)

        
        """
        api = self.EXT_API['dev1']
        try:
            balance = api.get_account_balance()
        except ApiException as e:
            self.assertEqual(e.status, 404)

    def test_ping(self):
        """
        Test case for ping

        
        """
        api = self.EXT_API['dev1']
        ping = api.ping("localhost")

    def test_post_block(self):
        """
        Test case for post_block

        
        """
        api = self.EXT_API['dev1']
        top = api.get_top()
        top_block = api.get_block_by_hash(top.hash)
        block_height = top_block.height + 1
        block = Block(height = block_height,
                prev_hash = top.hash,
                ## temporary
                state_hash = "6CN+HP79yKQYgD/GD3zfDb7Jcc9qp2MrHdzqxgoCxuQ=",
                ## temporary
                txs_hash = "VqLNlzhbj4qyzy/z9EweR+TtZyaJqWJYHnjckoBuYTM=",
                ## temporary
                target = 553713663,
                ## temporary
                nonce = block_height,
                time = utc_now(),
                version = 1,
                ## temporary
                pow = [311548,2065665,6108863,6269271,16501612,25441900,
                    26363511,26606249,27545581,29487162,31612335,40204159,
                    41283125,48945262,53014386,56739428,58119000,59077030,
                    60929609,61830792,72652230,72875797,74755966,76251602,
                    78469652,80969532,81248131,83068478,83633671,84203994,
                    85711118,89505851,90157562,90524633,96451406,99105008,
                    103724145,110979886,116332888,117754872,128960259,133685357
                    ],
                ## temporary
                transactions=[signed_coinbase_tx(block_height)]
                )
        api.post_block(block)
        print("Posted block " + str(block.height))

    def test_download_chain(self):
        """
        Test case for downloading the whole chain

        
        """
        api = self.EXT_API['dev1']
        top = api.get_top()
        block = api.get_block_by_hash(top.hash)
        while block.height != 0:
            print("Downloaded block " + str(block.height))
            block = api.get_block_by_hash(block.prev_hash)
        if block.height == 0:
            print("Downloaded genesis block")

if __name__ == '__main__':
    unittest.main()

