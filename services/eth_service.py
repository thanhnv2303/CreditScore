# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging
from datetime import datetime, timezone

import web3.eth
from web3 import Web3

from services.graph_operations import GraphOperations, OutOfBoundsError, Point


class EthService(object):
    def __init__(self, web3):
        graph = BlockTimestampGraph(web3)
        self._graph_operations = GraphOperations(graph)
        self.web3 = web3

    def get_block_range_for_date(self, date):
        start_datetime = datetime.combine(date, datetime.min.time().replace(tzinfo=timezone.utc))
        end_datetime = datetime.combine(date, datetime.max.time().replace(tzinfo=timezone.utc))
        return self.get_block_range_for_timestamps(start_datetime.timestamp(), end_datetime.timestamp())

    def get_block_range_for_timestamps(self, start_timestamp, end_timestamp):
        start_timestamp = int(start_timestamp)
        end_timestamp = int(end_timestamp)
        if start_timestamp > end_timestamp:
            raise ValueError('start_timestamp must be greater or equal to end_timestamp')

        try:
            start_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(start_timestamp)
        except OutOfBoundsError:
            start_block_bounds = (0, 0)

        try:
            end_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(end_timestamp)
        except OutOfBoundsError as e:
            raise OutOfBoundsError('The existing blocks do not completely cover the given time range') from e

        if start_block_bounds == end_block_bounds and start_block_bounds[0] != start_block_bounds[1]:
            raise ValueError('The given timestamp range does not cover any blocks')

        start_block = start_block_bounds[1]
        end_block = end_block_bounds[0]

        # The genesis block has timestamp 0 but we include it with the 1st block.
        if start_block == 1:
            start_block = 0

        return start_block, end_block

    def get_block_at_timestamp(self, timestamp):

        try:
            start_block_bounds = self._graph_operations.get_bounds_for_y_coordinate(timestamp)
        except OutOfBoundsError:
            start_block_bounds = (0, 0)

        return start_block_bounds[1]

    def get_latest_block(self):
        return self.web3.eth.blockNumber

    def get_balance(self, address, block_identifier="latest"):
        try:
            checksum_address = self.web3.toChecksumAddress(address)
            balance = self.web3.eth.getBalance(checksum_address, block_identifier=block_identifier)
            return balance
        except Exception as e:
            logging.getLogger("EthService").error(e)
            print(e)
            return None


class BlockTimestampGraph(object):
    def __init__(self, web3):
        self._web3 = web3

    def get_first_point(self):
        # Ignore the genesis block as its timestamp is 0
        return block_to_point(self._web3.eth.getBlock(1))

    def get_last_point(self):
        return block_to_point(self._web3.eth.getBlock('latest'))

    def get_point(self, x):
        return block_to_point(self._web3.eth.getBlock(x))


def block_to_point(block):
    return Point(block.number, block.timestamp)


# url = "http://25.19.185.225:8545"
# url = "https://bsc-dataseed.binance.org/"
# w3 = Web3(Web3.HTTPProvider(url))
# from web3.middleware import geth_poa_middleware
#
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)
#
# ethService = EthService(w3)
# print(ethService.get_block_range_for_timestamps(1602112735,1622112738))
# print(ethService.get_block_at_timestamp(1622112731))
