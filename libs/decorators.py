import logging


# Func which log func success result.
def log(func):
    def wrapper(*args, **kwargs):
        if not func(*args, **kwargs):
            logging.basicConfig(filename='tajga.log', level=logging.INFO,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.info('Success status: DONE')

    return wrapper


# Func which log func success result.
def write_log(func):
    def wrapper(*args, **kwargs):
        # if func(*args, **kwargs):
        #     logging.basicConfig(filename='tajga.log', level=logging.INFO,
        #                         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        #     logging.info('Success write data.')

        val = func(*args, **kwargs)
        logging.basicConfig(filename='tajga.log', level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info('Success write data from page {}.'.format(val))

    return wrapper

