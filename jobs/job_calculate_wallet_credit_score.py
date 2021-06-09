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

from database.database import Database
from executors.batch_work_executor import BatchWorkExecutor
from exporter.console_exporter import ConsoleExporter
from jobs.base_job import BaseJob
from services.credit_score_service_v_0_2_0 import CreditScoreServiceV020
from services.eth_service import EthService
from services.standardized_score_services import get_standardized_score_info

logger = logging.getLogger(__name__)
import datetime


class CalculateWalletCreditScoreJob(BaseJob):

    def __init__(
            self,
            web3,
            batch_size=24,
            max_workers=8,
            checkpoint=None,
            k_timestamp=None,
            item_exporter=ConsoleExporter(),
            database=Database(),
    ):
        self.item_exporter = item_exporter
        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.max_workers = max_workers
        self.paging = self.max_workers * 3
        self.web3 = web3
        self.database = database
        self.ethService = EthService(web3)
        self.end_block = self.ethService.get_latest_block()
        self.checkpoint = checkpoint
        if not self.checkpoint:
            now = datetime.datetime.now()
            self.checkpoint = str(now.year) + "-" + str(now.month) + "-" + str(now.day)

        if k_timestamp:
            self.start_block = self.ethService.get_block_at_timestamp(k_timestamp)
        else:
            self.start_block = self.end_block - 900000

        self.credit_score_services = CreditScoreServiceV020(database)
        self.statistics_credit = {}
        self._dict_cache = []

    def _start(self):
        self._calculate_standardized_score_info()
        self.item_exporter.open()

    def _calculate_standardized_score_info(self):
        statistics_credit = self.database.get_statistic_credit(self.checkpoint)
        # total_asset_list = list(statistics_credit.get('total_asset_list').values())
        total_asset_list = list(statistics_credit.get('total_asset_list'))
        total_asset_list_mean, total_asset_list_deviation = get_standardized_score_info(total_asset_list)

        # age_list = list(statistics_credit.get('age_list').values())
        age_list = list(statistics_credit.get('age_list'))
        age_list_mean, age_list_deviation = get_standardized_score_info(age_list)

        # value_of_transfer_to = list(statistics_credit.get('value_of_transfer_to').values())
        value_of_transfer_to = list(statistics_credit.get('value_of_transfer_to'))
        value_of_transfer_to_mean, value_of_transfer_to_deviation = get_standardized_score_info(value_of_transfer_to)

        # number_of_transfer = list(statistics_credit.get('number_of_transfer').values())
        number_of_transfer = list(statistics_credit.get('number_of_transfer'))
        number_of_transfer_mean, number_of_transfer_deviation = get_standardized_score_info(number_of_transfer)

        statistics_credit["total_asset_list_mean"] = str(total_asset_list_mean)
        statistics_credit["total_asset_list_deviation"] = str(total_asset_list_deviation)
        statistics_credit["age_list_mean"] = str(age_list_mean)
        statistics_credit["age_list_deviation"] = str(age_list_deviation)
        statistics_credit["value_of_transfer_to_mean"] = str(value_of_transfer_to_mean)
        statistics_credit["value_of_transfer_to_deviation"] = str(value_of_transfer_to_deviation)
        statistics_credit["number_of_transfer_mean"] = str(number_of_transfer_mean)
        statistics_credit["number_of_transfer_deviation"] = str(number_of_transfer_deviation)
        self.statistics_credit = statistics_credit
        self.database.update_statistic_credit(statistics_credit)

    def _export(self):
        skip = 0
        while True:
            wallets = self.database.get_wallets_credit_paging(skip=skip * self.paging, limit=self.paging)
            wallets = list(wallets)
            if len(wallets) == 0:
                return

            self.batch_work_executor.execute(
                wallets,
                self._export_batch,
                total_items=len(wallets)
            )
            skip = skip + 1

    def _export_batch(self, wallets):
        # handler work
        for wallet_data in wallets:
            # print(wallet_data)
            credit_score = self.credit_score_services.get_credit_score(wallet_data, self.statistics_credit)
            wallet_data["credit_score"] = credit_score
            # print("Credit score of wallet " + wallet_data.get("address") + " :" + str(credit_score))
            self.database.update_wallet_credit(wallet_data)
        pass

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()

    def get_cache(self):
        return self._dict_cache

    def clean_cache(self):
        self._dict_cache = []
