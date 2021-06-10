import logging


def config_log():
    format = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'
    logging.basicConfig(
        format=format,
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
