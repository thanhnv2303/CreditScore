from database.database import Database
from jobs.extractor.extractor import Extractor


class CirculatingAssetExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_address = wallet_data.get("address")
        wallet_credit = self.database.get_wallet_credit(wallet_address)
        if not wallet_credit:
            return
        self._supply_on_total_asset(wallet_data, wallet_credit)
        self._interest_on_supply(wallet_data, wallet_credit)

        # x41

    def _supply_on_total_asset(self, wallet_data, wallet_credit):
        pass

        # x42

    def _interest_on_supply(self, wallet_data, wallet_credit):
        pass
