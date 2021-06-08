from jobs.extractor.extractor import Extractor
from utils.to_number import to_int, to_float


class LoanRatioExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_address = wallet_data.get("address")
        wallet_credit = self.database.get_wallet_credit(wallet_address)
        if not wallet_credit:
            return

        block_number_order, lending_infos_usd = self.get_lending_infos_usd(wallet_credit)
        self._borrow_on_balance(block_number_order, lending_infos_usd, wallet_credit)
        self._borrow_on_supply(block_number_order, lending_infos_usd, wallet_credit)

    # x41
    def _borrow_on_balance(self, block_number_order, lending_infos_usd, wallet_credit):

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
            if balance_usd > 0 and end_block > start_block:
                avg_value += (borrow_usd / balance_usd) * (end_block - start_block)

            start_block = end_block
            i += 1

        avg_value = avg_value / (self.end_block - self.start_block)
        wallet_credit["borrow_on_balance"] = avg_value
        self.database.update_wallet_credit(wallet_credit)

    # x42
    def _borrow_on_supply(self, block_number_order, lending_infos_usd, wallet_credit):
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

            if supply_usd > 0 and end_block > start_block:
                avg_value += (borrow_usd / supply_usd) * (end_block - start_block)

            start_block = end_block
            i += 1

        avg_value = avg_value / (self.end_block - self.start_block)
        wallet_credit["borrow_on_supply"] = avg_value
        self.database.update_wallet_credit(wallet_credit)

    def get_lending_infos_usd(self, wallet_credit):
        lending_infos_usd = {}
        block_number_order = []

        lending_infos = wallet_credit.get("lending_infos")
        if lending_infos:
            for token in lending_infos:
                wallet_lending_token = wallet_credit.get("lending_infos").get(token)
                change_times = len(wallet_lending_token)
                for i in range(change_times):
                    balance = to_int(wallet_lending_token[i].get("balance"))
                    supply = to_int(wallet_lending_token[i].get("supply"))
                    borrow = to_int(wallet_lending_token[i].get("borrow"))
                    block_num_str = wallet_lending_token[i].get("block_number")
                    block_num_str = str(block_num_str)
                    balance_usd = self.credit_score_service.token_amount_to_usd(token, balance)
                    borrow_usd = self.credit_score_service.token_amount_to_usd(token, borrow)
                    supply_usd = self.credit_score_service.token_amount_to_usd(token, supply)
                    if not lending_infos_usd.get(block_num_str):
                        lending_infos_usd[block_num_str] = {
                            "balance": balance_usd,
                            "borrow": borrow_usd,
                            "supply": supply_usd,
                            "block_number": block_num_str
                        }
                        ## insert block number
                        j = 0
                        while (j < len(block_number_order) - 1):

                            if j == 0 and block_num_str < block_number_order[j]:
                                block_number_order.insert(0, block_num_str)
                                j = -1
                                break

                            if block_num_str > block_number_order[j] and block_num_str < block_number_order[j + 1]:
                                block_number_order.insert(j + 1, block_num_str)
                                j = -1
                                break
                            j += 1
                        if j == 0 or j == len(block_number_order) - 1:
                            block_number_order.append(block_num_str)
                    else:
                        lending_infos_usd[block_num_str]["balance"] += balance_usd
                        lending_infos_usd[block_num_str]["borrow"] += borrow_usd
                        lending_infos_usd[block_num_str]["supply"] += supply_usd

        for block_num_str in lending_infos_usd:
            lending_infos_usd[block_num_str]["balance"] = str(lending_infos_usd[block_num_str]["balance"])
            lending_infos_usd[block_num_str]["borrow"] = str(lending_infos_usd[block_num_str]["borrow"])
            lending_infos_usd[block_num_str]["supply"] = str(lending_infos_usd[block_num_str]["supply"])
        wallet_credit["block_number_order"] = block_number_order
        wallet_credit["lending_infos_usd"] = lending_infos_usd
        self.database.update_wallet_credit(wallet_credit)
        return block_number_order, lending_infos_usd
