import logging
import threading
import time

from database.database import Database
from database.memory_storage import MemoryStorage
from services.credit_score_service_v_0_2_0 import CreditScoreServiceV020

logger = logging.getLogger("--Extractor--")


class Extractor:
    def __init__(self, start_block, end_block, checkpoint, web3, database=Database()):
        self.web3 = web3
        self.database = database
        self.start_block = start_block
        self.end_block = end_block
        self.credit_score_service = CreditScoreServiceV020(database)
        self.checkpoint = checkpoint
        self.local_storage = MemoryStorage.getInstance()
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
        # self.lock.acquire()
        # if not self.statistic_credit.get(list_name):
        #     self.statistic_credit[list_name] = {}
        # if not self.statistic_credit.get("checkpoint"):
        #     self.statistic_credit["checkpoint"] = self.checkpoint
        #
        # self.statistic_credit[list_name][address] = value
        # start_time = time.time()
        # self.database.push_tolist_statistic_credit(self.checkpoint, list_name, value)
        list_value = self.local_storage.get_element(list_name)
        if not list_value:
            self.local_storage.add_element(list_name, [value])
        else:
            list_value.append(value)
        self.amount += 1
        # self.lock.release()

        # logger.info("Time to add static list" + str(time.time() - start_time))
        # logger.info(
        #     "num in static credit list name :" + list_name + " : " + str(len(self.local_storage.get_element(list_name))))
