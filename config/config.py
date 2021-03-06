"""
Module for the configurations of system
"""
import os


class Neo4jConfig:
    bolt = "bolt://0.0.0.0:7687"
    username = "neo4j"
    password = "trava_pass"


class Config:
    HOST = '0.0.0.0'
    PORT = 8000


class MongoDBConfig:
    NAME = os.environ.get("MONGO_USERNAME") or "just_for_dev"
    PASSWORD = os.environ.get("MONGO_PASSWORD") or "password_for_dev"
    # HOST = os.environ.get("MONGO_HOST") or "localhost"
    HOST = "25.19.185.225"
    PORT = os.environ.get("MONGO_PORT") or "27027"
    # PORT = os.environ.get("MONGO_PORT") or "27027"
    DATABASE = "EXTRACT_DATA_KNOWLEDGE_GRAPH"
    TRANSACTIONS = "TRANSACTIONS"
    TRANSACTIONS_TRANSFER = "TRANSACTIONS_TRANSFER"
    WALLET = "WALLET"
    POOL = "POOL"
    BLOCKS = "BLOCKS"
    TOKENS = "TOKENS"

    CREDIT_SCORE_DATABASE = "CREDIT_SCORE"
    WALLET_CREDIT = "WALLET_CREDIT"
    STATISTIC_CREDIT = "STATISTIC_CREDIT"


class Neo4jConfig:
    BOLT = "bolt://0.0.0.0:7687"
    HOST = os.environ.get("NEO4J_HOST") or "0.0.0.0"
    BOTH_PORT = os.environ.get("NEO4J_PORT") or 7687
    HTTP_PORT = os.environ.get("NEO4J_PORT") or 7474
    HTTPS_PORT = os.environ.get("NEO4J_PORT") or 7473
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME") or "neo4j"
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD") or "klg_pass"


class CreditScoreConfig:
    LOG_FILE = os.environ.get("CREDIT_SCORE_LOG_FILE")
    PROVIDER_URI = os.environ.get("CREDIT_SCORE_PROVIDER_URI")
    LAG = os.environ.get("CREDIT_SCORE_LAG") or 0
    BATCH_SIZE = os.environ.get("CREDIT_SCORE_BATCH_SIZE") or 64
    MAX_WORKERS = os.environ.get("CREDIT_SCORE_MAX_WORKERS") or 8
    START_BLOCK = os.environ.get("CREDIT_SCORE_START_BLOCK")
    PERIOD_SECONDS = os.environ.get("CREDIT_SCORE_PERIOD_SECONDS") or 10
    PID_FILE = os.environ.get("CREDIT_SCORE_PID_FILE") or None
    BLOCK_BATCH_SIZE = os.environ.get("CREDIT_SCORE_BLOCK_BATCH_SIZE") or 24
    TOKENS_FILTER_FILE = os.environ.get("CREDIT_SCORE_TOKENS_FILTER_FILE") or "artifacts/token_filter"
    EVENT_ABI_DIR = os.environ.get("CREDIT_SCORE_EVENT_ABI_DIR") or "artifacts/event-abi"
    LIST_TOKEN_FILTER = os.environ.get("CREDIT_SCORE_LIST_TOKEN_FILTER") or "artifacts/token_credit_info/listToken.txt"
    TOKEN_INFO = os.environ.get("CREDIT_SCORE_TOKEN_INFO") or "artifacts/token_credit_info/infoToken.json"
