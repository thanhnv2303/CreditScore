import threading

from database.database import Database
from services.credit_score_service_v_0_2_0 import CreditScoreServiceV020


class Extractor:
    def __init__(self, start_block, end_block, checkpoint, web3, database=Database()):
        self.web3 = web3
        self.database = database
        self.start_block = start_block
        self.end_block = end_block
        self.credit_score_service = CreditScoreServiceV020(database)
        self.checkpoint = checkpoint
        self.statistic_credit = {}
        self.lock = threading.Lock()
        self.amount = 0

    def extract(self, data):
        pass

    def save_statistic_credit(self):
        # print(self.statistic_credit)
        if self.statistic_credit:
            self.statistic_credit["checkpoint"] = self.checkpoint
            self.database.update_statistic_credit(statistic_credit=self.statistic_credit)

    def add_to_statistic_list(self, list_name, address, value):
        self.lock.acquire()
        if not self.statistic_credit.get(list_name):
            self.statistic_credit[list_name] = {}
        if not self.statistic_credit.get("checkpoint"):
            self.statistic_credit["checkpoint"] = self.checkpoint

        self.statistic_credit[list_name][address] = value
        self.database.update_statistic_credit(self.statistic_credit)
        self.amount += 1
        self.lock.release()
