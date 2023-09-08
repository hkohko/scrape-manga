import logging


class Logger:
    def __init__(self):
        log_format = "%(asctime)s:%(levelname)s:%(message)s"
        self.basic_logger = logging.basicConfig(format=log_format, level=logging.INFO)
