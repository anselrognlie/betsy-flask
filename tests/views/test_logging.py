from betsy.logging.logger import logger

def test_log_exception():
    try:
        raise RuntimeError('some error')
    except RuntimeError:
        logger.exception('test runtime error logging')
