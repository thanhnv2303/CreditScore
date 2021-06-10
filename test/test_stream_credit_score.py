import os
import sys

TOP_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(TOP_DIR, './'))

import logging

format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
logging.basicConfig(
    format=format,
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

from providers.auto import pick_random_provider_uri
from streaming.credit_score_streamer import CreditScoreStreamer
from streaming.streamer_adapter.credit_score_streamer_adapter import CreditScoreStreamerAdapter

provider_uri = "http://25.19.185.225:8545"

provider_uri = pick_random_provider_uri(provider_uri)
logging.info('Using ' + provider_uri)

streamer_adapter = CreditScoreStreamerAdapter(provider_uri)
streamer = CreditScoreStreamer(
    blockchain_streamer_adapter=streamer_adapter,
    pid_file=None
)
streamer.stream()
