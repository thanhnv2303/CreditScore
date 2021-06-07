import datetime
import logging

from web3 import Web3
from web3.middleware import geth_poa_middleware

from database.database import Database
from exporter.console_exporter import ConsoleExporter
from jobs.job_calculate_wallet_credit_score import CalculateWalletCreditScoreJob
from jobs.job_extract_credit_data import ExtractCreditDataJob
from providers.auto import pick_random_provider_uri, get_provider_from_uri
from services.credit_score_service_v_0_2_0 import CreditScoreServiceV020
from services.get_k_timestamp import get_k_timestamp
from utils.thread_local_proxy import ThreadLocalProxy


class CreditScoreStreamerAdapter:
    def __init__(
            self,
            provider_uri,
            batch_size=128,
            max_workers=8,
            checkpoint=None,
            item_exporter=ConsoleExporter(),
            database=Database()):
        self.item_exporter = item_exporter

        self.max_workers = max_workers
        self.paging = self.max_workers * 3
        self.database = database
        self.batch_size = batch_size

        self.k_timestamp = get_k_timestamp()
        self.checkpoint = checkpoint
        if not self.checkpoint:
            now = datetime.datetime.now()
            self.checkpoint = str(now.year) + "-" + str(now.month) + "-" + str(now.day)

        self.provider_uri = pick_random_provider_uri(provider_uri)

        batch_web3_provider = ThreadLocalProxy(lambda: get_provider_from_uri(self.provider_uri, batch=True))

        w3 = Web3(batch_web3_provider)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.w3 = w3

        self.logger = logging.getLogger('CreditScoreStreamerAdapter')
        self._dict_cache = []

    def open(self):
        pass

    def get_current_block_number(self):
        return int(self.w3.eth.getBlock("latest").number)

    def export_all(self, start_block, end_block):
        token_service = CreditScoreServiceV020()
        token_service.update_token_market_info()

        job_extract = ExtractCreditDataJob(web3=self.w3,
                                           batch_size=128,
                                           max_workers=8,
                                           checkpoint=self.checkpoint,
                                           k_timestamp=self.k_timestamp,
                                           item_exporter=ConsoleExporter(),
                                           database=self.database)
        job_extract.run()

        job_calculate_credit_score = CalculateWalletCreditScoreJob(web3=self.w3,
                                                                   batch_size=128,
                                                                   max_workers=8,
                                                                   checkpoint=self.checkpoint,
                                                                   k_timestamp=self.k_timestamp,
                                                                   item_exporter=ConsoleExporter(),
                                                                   database=self.database)
        job_calculate_credit_score.run()

    def close(self):
        pass
