import datetime
import json
import logging
import os

from database.database import Database
from services.update_date_token_credit_score import update_token_credit_score
from utils.to_number import to_int, to_float


class CreditScoreServiceV020:
    BNB = "0x"

    def __init__(self, database=Database(), list_token_filter="../artifacts/token_credit_info/listToken.txt",
                 token_info="../artifacts/token_credit_info/infoToken.json"):
        self.database = database
        self.fix_prices = {
            "0x": {
                "price": 343.30,  ### fix price for BNB
                "decimals": 18
            }
        }

        cur_path = os.path.dirname(os.path.realpath(__file__))
        path_market = cur_path + "/" + token_info

        with open(path_market, "r") as file:
            try:
                self.tokens_market = json.load(file)
            except:
                self.update_token_market_info(fileInput=list_token_filter, fileOutput=token_info)
                with open(path_market, "r") as file:
                    self.tokens_market = json.load(file)

        self.tokens_market["0x"] = {
            "symbol": "BNB",
            "price": "380.17",
            "credit_score": 1000.0,
            "market_cap": 7555675507.00,
            "decimals": 18
        }

        self.balance_threshold = 1000
        self.supply_threshold = 1000
        self.threshold = 1000
        self.total_borrow_threshold = 100

        self.logger = logging.getLogger('CreditScoreServiceV0.2.0')

    def token_amount_to_usd(self, token_address, amount):
        token = self.tokens_market.get(token_address)
        if not token:
            return 0
        decimals = to_int(token.get("decimals"))
        price = to_float(token.get("price"))

        return to_int(amount) * price / 10 ** decimals

    def get_credit_score(self, wallet, statistics_credit=None):
        if not statistics_credit:
            now = datetime.datetime.now()
            checkpoint = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
            statistics_credit = self.database.get_statistic_credit(checkpoint)

        ### 1 Tổng tài sản - Total asset

        x1 = self._get_x1(wallet, statistics_credit)
        a1 = 0.25

        ### 2 Lịch sử tín dụng - Payment history

        x21 = self._get_x21(wallet, statistics_credit)
        x22 = self._get_x22(wallet, statistics_credit)
        x23 = self._get_x23(wallet, statistics_credit)
        x24 = self._get_x24(wallet, statistics_credit)

        a2 = 0.35
        b21 = 0.3
        b22 = 0.3
        b23 = 0.2
        b24 = 0.2

        x2 = b21 * x21 + b22 * x22 + b23 * x23 + b24 * x24

        ### 3 Tỷ lệ nợ - loan ratio
        x31 = self._get_x31(wallet, statistics_credit)
        x32 = self._get_x32(wallet)

        a3 = 0.15
        b31 = 0.6
        b32 = 0.4

        x3 = b31 * x31 + b32 * x32

        ### 4 Tỷ lệ tài sản lưu thông - Circulating asset
        x41 = self._get_x41(wallet)
        x42 = self._get_x42(wallet)

        a4 = 0.2
        b41 = 0.5
        b42 = 0.5

        x4 = b41 * x41 + b42 * x42

        ### .5 Tài sản số - Digital asset : 4=0.1

        x51 = self._get_x51(wallet)
        x52 = self._get_x52(wallet)

        a5 = 0.05
        b51 = 0.6
        b52 = 0.4

        x5 = b51 * x51 + b52 * x52

        ### credit score
        credit_score = a1 * x1 + a2 * x2 + a3 * x3 + a4 * x4 + a5 * x5
        return credit_score

    ### Total asset
    def _get_x1(self, wallet, statistics_credit):
        try:
            total_asset_list_mean = to_float(statistics_credit["total_asset_list_mean"])
            total_asset_list_deviation = to_float(statistics_credit["total_asset_list_deviation"])
            total_asset = to_float(wallet.get("total_asset"))
            return (total_asset - total_asset_list_mean) / total_asset_list_deviation
        except Exception as e:
            # self.logger.error(e)
            self.logger.error(e)
            return 0

    ### x21: là tuổi thọ của account
    def _get_x21(self, wallet, statistics_credit):
        try:
            age_list_mean = to_float(statistics_credit["age_list_mean"])
            age_list_deviation = to_float(statistics_credit["age_list_deviation"])
            age = to_float(wallet.get("age"))
            return (age - age_list_mean) / age_list_deviation

        except Exception as e:
            # self.logger.error(e)
            self.logger.error(e)
            return 0

    ### x22: được tính dựa trên tỷ lệ số lần bị thanh lý khoản vay trên tổng số lần vay
    def _get_x22(self, wallet, statistics_credit):
        try:
            lending_infos_usd = wallet.get("lending_infos_usd")
            if not lending_infos_usd:
                return 0
            total_borrow = 0
            for block in lending_infos_usd:
                total_borrow += to_float(lending_infos_usd[block].get("borrow"))
            if total_borrow < self.total_borrow_threshold:
                return 0
            number_of_liquidate = to_float(statistics_credit["number_of_liquidate"])
            number_of_borrow = to_float(statistics_credit["number_of_borrow"])
            return (1 - (number_of_liquidate / number_of_borrow)) * self.threshold

        except Exception as e:
            self.logger.error(e)
            return 0

    ### x23: tổng lượng tiền giao dịch của account
    def _get_x23(self, wallet, statistics_credit):
        try:
            value_of_transfer_to_mean = to_float(statistics_credit["value_of_transfer_to_mean"])
            value_of_transfer_to_deviation = to_float(statistics_credit["value_of_transfer_to_deviation"])
            value_of_transfer_to = to_float(wallet.get("value_of_transfer_to"))
            return (value_of_transfer_to - value_of_transfer_to_mean) / value_of_transfer_to_deviation

        except Exception as e:
            self.logger.error(e)
            return 0

    ### x24: tổng lượng tiền giao dịch của account
    def _get_x24(self, wallet, statistics_credit):
        try:
            number_of_transfer_mean = to_float(statistics_credit["number_of_transfer_mean"])
            number_of_transfer_deviation = to_float(statistics_credit["number_of_transfer_deviation"])
            number_of_transfer = to_float(wallet.get("number_of_transfer"))
            return (number_of_transfer - number_of_transfer_mean) / number_of_transfer_deviation

        except Exception as e:
            self.logger.error(e)
            return 0

    ### x31 :  Tỷ lệ nợ trên số dư ví,
    def _get_x31(self, wallet, statistics_credit):
        try:
            borrow_on_balance = to_float(wallet.get('borrow_on_balance'))
            borrow_on_supply = to_float(wallet.get('borrow_on_supply'))
            supply_on_total_asset = to_float(wallet.get('supply_on_total_asset'))
            if borrow_on_balance == 0 and borrow_on_supply == 0 and supply_on_total_asset == 0:
                return 0

            return (1 - min(1, borrow_on_balance)) * self.threshold

        except Exception as e:
            self.logger.error(e)
            return 0

    ###x32: tỷ lệ nợ trên số tiền đầu tư,
    def _get_x32(self, wallet):
        try:
            borrow_on_balance = to_float(wallet.get('borrow_on_balance'))
            borrow_on_supply = to_float(wallet.get('borrow_on_supply'))
            supply_on_total_asset = to_float(wallet.get('supply_on_total_asset'))
            if borrow_on_balance == 0 and borrow_on_supply == 0 and supply_on_total_asset == 0:
                return 0

            return (1 - min(1, borrow_on_supply)) * self.threshold

        except Exception as e:
            self.logger.error(e)
            return 0

    ### x41 : tỷ lệ tiền đang đầu tư trên tổng tài sản,
    def _get_x41(self, wallet):
        try:
            borrow_on_balance = to_float(wallet.get('borrow_on_balance'))
            borrow_on_supply = to_float(wallet.get('borrow_on_supply'))
            supply_on_total_asset = to_float(wallet.get('supply_on_total_asset'))
            if borrow_on_balance == 0 and borrow_on_supply == 0 and supply_on_total_asset == 0:
                return 0

            return supply_on_total_asset * self.threshold

        except Exception as e:
            self.logger.error(e)
            return 0

    ### x42 : ROE - Hiệu suất sinh lời trên tổng vốn đầu tư-
    def _get_x42(self, wallet):
        return 0

    ### x51: Token score - Điểm tín dụng cho Token, c
    def _get_x51(self, wallet):
        if not wallet.get("balances"):
            return 0
        balances = wallet.get("balances")
        token_score_wallet = 0
        for token_address in balances:
            if not self.tokens_market.get(token_address):
                continue

            token_score = self.tokens_market.get(token_address).get("credit_score")
            # print(token_score)
            token_score_wallet = max(token_score_wallet, token_score)

        return token_score_wallet

    ### x52 :  NFT score - Điểm tín dụng cho NFT,
    def _get_x52(self, wallet):
        return 0

    def update_token_market_info(self, fileInput='../artifacts/token_credit_info/listToken.txt',
                                 fileOutput='../artifacts/token_credit_info/infoToken.json'):
        update_token_credit_score(fileInput=fileInput, fileOutput=fileOutput, database=self.database)
        return 0

    def test_print(self, address):
        wallet = self.database.get_wallet(address)

        print(self._get_x51(wallet))


"""
keep acc 
0x00b23015762b310421e8f940b97f4180d084dda1
0xe2477627fa2db8ba2a4fe467876023987c3a7e8e
0xe2477627fa2db8ba2a4fe467876023987c3a7e8e

0x956bce4f086dc4579b960ed80336ef79737cdaa3
0x48620b6a00ff75d17082c81bd97896517332c6fe

781629306315660
663171985091646
"""


# credi = CreditScoreService()
# score = credi.test_print("0x0d0707963952f2fba59dd06f2b425ace40b492fe")
# print("score")
# print(score)


class TokenMarketInfo:
    name = ""
    address = ""
    symbol = ""
    price_coin = 0
    market_rank = 0
    highest_price = 0
    market_cap = 0
