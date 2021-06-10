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

logger = logging.getLogger("CreditScoreStreamerAdapter")


class CreditScoreStreamerAdapter:
    def __init__(
            self,
            provider_uri,
            batch_size=128,
            max_workers=8,
            checkpoint=None,
            item_exporter=ConsoleExporter(),
            database=Database(),
            list_token_filter="artifacts/token_credit_info/listToken.txt",
            token_info="artifacts/token_credit_info/infoToken.json"
    ):
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

        self.list_token_filter = list_token_filter
        self.token_info = token_info

    def open(self):
        pass

    def get_current_block_number(self):
        return int(self.w3.eth.getBlock("latest").number)

    def export_all(self, start_block, end_block):
        logger.info("Update token market info")
        token_service = CreditScoreServiceV020(self.database, self.list_token_filter, self.token_info)
        token_service.update_token_market_info(fileInput=self.list_token_filter, fileOutput=self.token_info)

        logger.info("-------------------------------------------------------------")
        logger.info("ExtractCreditDataJob ")
        job_extract = ExtractCreditDataJob(web3=self.w3,
                                           batch_size=self.batch_size,
                                           max_workers=self.max_workers,
                                           checkpoint=self.checkpoint,
                                           k_timestamp=self.k_timestamp,
                                           item_exporter=ConsoleExporter(),
                                           database=self.database)
        job_extract.run()

        logger.info("-------------------------------------------------------------")
        logger.info("CalculateWalletCreditScoreJob ")
        job_calculate_credit_score = CalculateWalletCreditScoreJob(web3=self.w3,
                                                                   batch_size=self.batch_size,
                                                                   max_workers=self.max_workers,
                                                                   checkpoint=self.checkpoint,
                                                                   k_timestamp=self.k_timestamp,
                                                                   item_exporter=ConsoleExporter(),
                                                                   database=self.database,
                                                                   list_token_filter=self.list_token_filter,
                                                                   token_info=self.token_info
                                                                   )
        job_calculate_credit_score.run()

    def close(self):
        pass
