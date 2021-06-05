import math

from jobs.extractor.extractor import Extractor


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
        pass

    # x23 ,x24 - total amount token transfer and the num of transfer in k days
    def _extract_transfer(self, wallet_data, wallet_credit):
        pass
