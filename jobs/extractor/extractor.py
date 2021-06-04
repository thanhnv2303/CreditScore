import threading

from database.database import Database
from services.credit_score_service import CreditScoreService


class Extractor:
    def __init__(self, start_block, end_block, checkpoint, web3, database=Database()):
        self.web3 = web3
        self.database = database
        self.start_block = start_block
        self.end_block = end_block
        self.credit_score_service = CreditScoreService(database)
        self.checkpoint = checkpoint
        self.statistic_credit = {}
        self.lock = threading.Lock()

    def extract(self, data):
        pass

    def save_statistic_credit(self):
        # print(self.statistic_credit)
        if self.statistic_credit:
            self.statistic_credit["checkpoint"] = self.checkpoint
            self.database.update_statistic_credit(statistic_credit=self.statistic_credit)