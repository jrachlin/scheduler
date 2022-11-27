import time
import random
import logging

logger = logging.getLogger(__name__)

logger.info('I am running the task failure script.')
sleep_time = random.randint(1,3)
time.sleep(sleep_time)
raise Exception('Test Exception')
