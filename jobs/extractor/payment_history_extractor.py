import math

from jobs.extractor.extractor import Extractor
from utils.to_number import to_int


class PaymentHistoryExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_address = wallet_data.get("address")
        wallet_credit = self.database.get_wallet_credit(wallet_address)
        if not wallet_credit:
            return
        self._extract_age(wallet_data, wallet_credit)
        self._extract_borrow(wallet_data, wallet_credit)
        self._extract_transfer(wallet_data, wallet_credit)
        pass

    # x21
    def _extract_age(self, wallet_data, wallet_credit):
        wallet_address = wallet_data.get("address")

        age = wallet_credit.get("age")
        if not age:
            age = math.inf
        lending_infos = wallet_data.get("lending_infos")
        if lending_infos:
            for token in lending_infos:
                token_age = lending_infos[token][0].get("block_number")
                age = min(token_age, age)
        accumulate_history = wallet_data.get("accumulate_history")
        if accumulate_history:
            for event in accumulate_history:
                for token in accumulate_history[event]:
                    token_age = accumulate_history[event][token][0].get("block_number")
                    age = min(token_age, age)
        wallet_credit["age"] = age

        self.database.update_wallet_credit(wallet_credit)

        list_name = "age_list"
        self.add_to_statistic_list(list_name, wallet_address, age)
        pass

    # x22 the num of -liquidate -borrow
    def _extract_borrow(self, wallet_data, wallet_credit):
        wallet_address = wallet_data.get("address")
        accumulate_history = wallet_data.get("accumulate_history")
        number_of_liquidate = 0
        number_of_borrow = 0
        value_of_borrow_accumulate = 0
        if accumulate_history:
            if accumulate_history.get("Borrow"):
                borrows = accumulate_history.get("Borrow")
                for token_address in borrows:
                    number_of_borrow += len(borrows[token_address])
                    accumulate_amount = to_int(borrows[token_address][-1].get("accumulate_amount"))
                    value_of_borrow_accumulate += self.credit_score_service.token_amount_to_usd(token_address,
                                                                                                accumulate_amount)
            if accumulate_history.get("LiquidateBorrow-borrower"):
                liquidateBorrowers = accumulate_history.get("LiquidateBorrow-borrower")
                for token_address in liquidateBorrowers:
                    number_of_liquidate += len(liquidateBorrowers[token_address])
        wallet_credit["number_of_liquidate"] = number_of_liquidate
        wallet_credit["number_of_borrow"] = number_of_borrow
        wallet_credit["value_of_borrow_accumulate"] = value_of_borrow_accumulate
        self.database.update_wallet_credit(wallet_credit)
        list_name = "number_of_liquidate"
        self.add_to_statistic_list(list_name, wallet_address, number_of_liquidate)
        list_name = "number_of_borrow"
        self.add_to_statistic_list(list_name, wallet_address, number_of_borrow)
        list_name = "value_of_borrow_accumulate"
        self.add_to_statistic_list(list_name, wallet_address, value_of_borrow_accumulate)

    # x23 ,x24 - total amount token transfer to and the num of transfer in k days
    def _extract_transfer(self, wallet_data, wallet_credit):
        wallet_address = wallet_data.get("address")
        accumulate_history = wallet_data.get("accumulate_history")
        value_of_transfer_to = 0
        number_of_transfer = 0

        if accumulate_history:
            if accumulate_history.get("TransferTo"):
                transfer_to = accumulate_history.get("TransferTo")
                transfer_to_credit = wallet_credit.get("accumulate_history").get("TransferTo")
                for token_address in transfer_to:
                    i = 0
                    while i < len(transfer_to[token_address]):
                        block_num = transfer_to[token_address][i].get("block_number")
                        if block_num >= self.start_block:
                            break
                        i = i + 1
                    transfer_to_credit[token_address] = transfer_to[token_address][i:]
                    if len(transfer_to[token_address]) == 1:
                        checkpoint_amount = 0
                    else:
                        checkpoint_amount = to_int(transfer_to[token_address][0].get("accumulate_amount"))
                    amount_of_transfer_to = to_int(
                        transfer_to[token_address][-1].get("accumulate_amount")) - checkpoint_amount
                    value_of_transfer_to += self.credit_score_service.token_amount_to_usd(token_address,
                                                                                          amount_of_transfer_to)
                    number_of_transfer += len(transfer_to[token_address])

            if accumulate_history.get("TransferFrom"):
                transfer_from = accumulate_history.get("TransferFrom")
                transfer_from_credit = wallet_credit.get("accumulate_history").get("TransferFrom")
                for token_address in transfer_from:
                    i = 0
                    while i < len(transfer_from[token_address]):
                        block_num = transfer_from[token_address][i].get("block_number")
                        if block_num >= self.start_block:
                            break
                        i = i + 1
                    transfer_from_credit[token_address] = transfer_from[token_address][i:]
                    number_of_transfer += len(transfer_from[token_address])

        wallet_credit["value_of_transfer_to"] = value_of_transfer_to
        wallet_credit["number_of_transfer"] = number_of_transfer
        self.database.update_wallet_credit(wallet_credit)
        list_name = "value_of_transfer_to"
        self.add_to_statistic_list(list_name, wallet_address, value_of_transfer_to)
        list_name = "number_of_transfer"
        self.add_to_statistic_list(list_name, wallet_address, number_of_transfer)
