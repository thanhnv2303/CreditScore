from jobs.extractor.extractor import Extractor
from utils.to_number import to_float, to_int


class CirculatingAssetExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_address = wallet_data.get("address")
        wallet_credit = self.database.get_wallet_credit(wallet_address)
        if not wallet_credit:
            return

        block_number_order = wallet_credit.get("block_number_order")
        lending_infos_usd = wallet_credit.get("lending_infos_usd")
        self._supply_on_total_asset(block_number_order, lending_infos_usd, wallet_credit)
        self._interest_on_supply(block_number_order, lending_infos_usd, wallet_credit)

        # x41

    def _supply_on_total_asset(self, block_number_order, lending_infos_usd, wallet_credit):
        change_times = len(block_number_order)
        avg_value = 0
        start_block = to_int(self.start_block)
        i = 0
        while i < change_times:
            if i == change_times - 1:
                end_block = self.end_block
            else:
                end_block = block_number_order[i + 1]
            end_block = to_int(end_block)
            block_number_str = str(block_number_order[i])
            balance_usd = to_float(lending_infos_usd[block_number_str].get("balance"))
            borrow_usd = to_float(lending_infos_usd[block_number_str].get("borrow"))
            supply_usd = to_float(lending_infos_usd[block_number_str].get("supply"))
            total_asset = balance_usd + supply_usd - borrow_usd
            if total_asset > 0 and end_block > start_block:
                avg_value += (supply_usd / total_asset) * (end_block - start_block)

            start_block = end_block
            i += 1

        avg_value = avg_value / (self.end_block - self.start_block)
        wallet_credit["supply_on_total_asset"] = avg_value
        self.database.update_wallet_credit(wallet_credit)

        # x42

    def _interest_on_supply(self, block_number_order, lending_infos_usd, wallet_credit):
        pass
