import logging

class StdoutLogger:
    def exception(self, *args, **kwargs):
        logging.exception(*args, **kwargs)
