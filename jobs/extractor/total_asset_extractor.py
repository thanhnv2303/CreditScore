from database.database import Database
from jobs.extractor.extractor import Extractor
from utils.to_number import to_int


class TotalAssetExtractor(Extractor):
    def __init__(self, start_block, end_block, checkpoint, web3, database=Database()):
        super(TotalAssetExtractor, self).__init__(start_block, end_block, checkpoint, web3, database)
        self.statistic_credit["total_asset_list"] = {}
        self.statistic_credit_lock = False

    def extract(self, wallet_data):
        address = wallet_data.get("address")
        if not wallet_data.get("balances") and not wallet_data.get("lending_info"):
            # self.database.delete_wallet(address)
            return
        ### get wallet at credit database
        wallet_credit = self.database.get_wallet_credit(address)
        if not wallet_credit:
            wallet_credit = wallet_data

        ### get info credit from start_block to end_block

        ### pruning info out of range start block and end block
        if not wallet_credit.get("lending_infos"):
            return
        for address in wallet_credit.get("lending_infos"):
            i = 0
            lending_info_address = wallet_credit.get("lending_infos")[address]
            while i < len(lending_info_address):
                block_num = lending_info_address[i].get("block_number")
                if block_num >= self.start_block:
                    break
                i = i + 1
            wallet_credit.get("lending_infos")[address] = lending_info_address[i:]

        for address in wallet_data.get("lending_infos"):
            lending_info_address = wallet_data.get("lending_infos")[address]
            i = len(lending_info_address) - 1
            latest_block_wallet_credit_address = wallet_credit.get("lending_infos").get(address)[-1].get("block_number")

            while i >= 0:
                block_num = lending_info_address[i].get("block_number")
                if block_num <= latest_block_wallet_credit_address:
                    break
                i = i - 1
            if i == -1:
                i = 0
            wallet_credit.get("lending_infos")[address] += lending_info_address[i:]

        total_asset = 0
        for address in wallet_credit.get("lending_infos"):
            wallet_lending_token = wallet_credit.get("lending_infos").get(address)

            start_block = self.start_block
            change_times = len(wallet_lending_token)
            avg_value = 0
            for i in range(change_times):
                balance = to_int(wallet_lending_token[i].get("balance"))
                supply = to_int(wallet_lending_token[i].get("supply"))
                borrow = to_int(wallet_lending_token[i].get("borrow"))
                amount = balance + supply - borrow

                if i == change_times - 1:
                    end_block = self.end_block
                else:
                    end_block = wallet_lending_token[i + 1].get("block_number")
                accumulate_value = self.credit_score_service.token_amount_to_usd(address, amount) * (
                        end_block - start_block)
                if accumulate_value > 0:
                    avg_value += accumulate_value
                start_block = end_block
            avg_value = avg_value / (self.end_block - self.start_block)

            total_asset += avg_value

        wallet_credit["total_asset"] = total_asset
        if total_asset <= 0:
            return
        ### update other info
        wallet_credit["at_block_number"] = wallet_data.get("at_block_number")
        wallet_credit["balances"] = wallet_data.get("balances")
        wallet_credit["transactions"] = wallet_data.get("transactions")
        wallet_credit["accumulate"] = wallet_data.get("accumulate")
        wallet_credit["accumulate_history"] = wallet_data.get("accumulate_history")
        wallet_credit["lending_info"] = wallet_data.get("lending_info")

        self.database.update_wallet_credit(wallet_credit)

        list_name = "total_asset_list"
        wallet_address = wallet_data.get("address")

        self.add_to_statistic_list(list_name, wallet_address, total_asset)

        # self.lock.acquire()
        # if not self.statistic_credit.get("total_asset_list"):
        #     self.statistic_credit["total_asset_list"] = {}
        # if not self.statistic_credit.get("checkpoint"):
        #     self.statistic_credit["checkpoint"] = self.checkpoint
        #
        # self.statistic_credit["total_asset_list"][wallet_data.get("address")] = total_asset
        # self.database.update_statistic_credit(self.statistic_credit)
        # self.lock.release()
