import logging

def log(log, type):
    if type is 'w':
        logging.warning(log)
    if type is 'i':
        logging.info(log)
    if type is 'e':
        logging.error(log)        