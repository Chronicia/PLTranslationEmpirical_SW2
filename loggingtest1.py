import logging

def log_test():
    logging.basicConfig(filename="logs/translation.log", level=logging.DEBUG)
    logging.info('This message should also go to the log file')

log_test()