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
from jobs.extractor.circulating_asset_extractor import CirculatingAssetExtractor
from jobs.extractor.digital_asset_extractor import DigitalAssetExtractor
from jobs.extractor.loan_ratio_extractor import LoanRatioExtractor
from jobs.extractor.payment_history_extractor import PaymentHistoryExtractor
from jobs.extractor.total_asset_extractor import TotalAssetExtractor
from services.eth_service import EthService

logger = logging.getLogger(__name__)
import datetime


class ExtractCreditDataJob(BaseJob):
    def _start(self):
        self.item_exporter.open()

    def __init__(
            self,
            web3,
            batch_size=128,
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
        if k_timestamp:

            self.start_block = self.ethService.get_block_at_timestamp(k_timestamp)
        else:
            self.start_block = self.end_block - 900000

        self.extractors = []
        self._add_extractor()

        self._dict_cache = []

    def _add_extractor(self):
        if not self.checkpoint:
            now = datetime.datetime.now()
            checkpoint = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
        else:
            checkpoint = self.checkpoint

        self.extractors.append(
            TotalAssetExtractor(self.start_block, self.end_block, checkpoint, self.web3, self.database))
        self.extractors.append(
            PaymentHistoryExtractor(self.start_block, self.end_block, checkpoint, self.web3, self.database))
        self.extractors.append(
            LoanRatioExtractor(self.start_block, self.end_block, checkpoint, self.web3, self.database))
        self.extractors.append(
            CirculatingAssetExtractor(self.start_block, self.end_block, checkpoint, self.web3, self.database))
        self.extractors.append(
            DigitalAssetExtractor(self.start_block, self.end_block, checkpoint, self.web3, self.database))

        statistic_credit = {
            "checkpoint": checkpoint
        }
        self.database.delete_statistic_credit(checkpoint)
        self.database.update_statistic_credit(statistic_credit)

    def _export(self):
        skip = 0
        while True:
            wallets = self.database.get_wallets_paging(skip=skip * self.paging, limit=self.paging)
            wallets = list(wallets)
            if len(wallets) == 0:
                return
            self.batch_work_executor.execute(
                wallets,
                self._export_batch
            )
            skip = skip + 1

    def _export_batch(self, wallets):
        # handler work
        for wallet_data in wallets:
            for extractor in self.extractors:
                extractor.extract(wallet_data)

        pass

    def _end(self):
        self.batch_work_executor.shutdown()
        self.item_exporter.close()

    def get_cache(self):
        return self._dict_cache

    def clean_cache(self):
        self._dict_cache = []
