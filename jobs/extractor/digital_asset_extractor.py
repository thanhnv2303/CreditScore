from jobs.extractor.extractor import Extractor


class DigitalAssetExtractor(Extractor):

    def extract(self, wallet_data):
        wallet_data["checkpoint"] = self.checkpoint
        self.database.update_wallet(wallet_data)
        pass
