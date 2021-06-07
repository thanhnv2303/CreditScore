from jobs.extractor.extractor import Extractor


class LoanRatioExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_address = wallet_data.get("address")
        wallet_credit = self.database.get_wallet_credit(wallet_address)
        if not wallet_credit:
            return
        self._borrow_on_total_asset(wallet_data, wallet_credit)
        self._borrow_on_supply(wallet_data, wallet_credit)

    # x41
    def _borrow_on_total_asset(self, wallet_data, wallet_credit):
        pass

    # x42
    def _borrow_on_supply(self, wallet_data, wallet_credit):
        pass
