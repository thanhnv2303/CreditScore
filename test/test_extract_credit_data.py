import os

from web3 import Web3
from web3.middleware import geth_poa_middleware

from jobs.job_extract_credit_data import ExtractCreditDataJob
from providers.auto import get_provider_from_uri, pick_random_provider_uri
from utils.thread_local_proxy import ThreadLocalProxy

if __name__ == '__main__':

    batch_size = 128
    max_workers = 8
    from os.path import expanduser

    home = expanduser("~")
    geth_ipc_file = home + "/bsc-full-sync/node/geth.ipc"
    if not os.path.exists(geth_ipc_file):
        provider_uri = "http://25.19.185.225:8545"
        provider_uri = "https://bsc-dataseed.binance.org/"
    else:
        provider_uri = "file:///" + geth_ipc_file

    provider_uri = pick_random_provider_uri(provider_uri)

    batch_web3_provider = ThreadLocalProxy(lambda: get_provider_from_uri(provider_uri, batch=True))

    w3 = Web3(batch_web3_provider)
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    k_timestamp = 1613001794
    job_extract = ExtractCreditDataJob(web3=w3, k_timestamp=k_timestamp)
    job_extract.run()
