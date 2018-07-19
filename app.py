import logging
import sys
import schedule
from datetime import datetime

import pandas

from model.chat_message import ChatMessage
from preprocessing.preprocessing import Preprocessing

# init logger
logger = logging.getLogger("goliath")

# init our Preprocessing
preprocessing = Preprocessing(logger)

merchant_name = ""
current_month = ""
current_year = ""


def init_logger():
    """
    Init logger.
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    logfile_handler = logging.StreamHandler(stream=sys.stdout)
    logfile_handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logfile_handler)


def get_chat_message_history(month, year):
    """
    Get chat history based on year and month.

    :param month: month. example value 8.
    :param year: year. example value 2018.
    :return: list of ChatMessage.
    """
    chat_message_list_raw = pandas.read_csv('./resource/example/example.csv', sep=',')
    chat_message_list = list()

    if not chat_message_list_raw.empty:
        logger.info('Succeeded get chat message, total message %s' % len(chat_message_list_raw.values))

        for item in chat_message_list_raw.values:
            chat_message = ChatMessage(name=item[0],
                                       content=item[1],
                                       create_at=item[2],
                                       channel=item[3],
                                       sender_role=item[4],
                                       sender_id=item[5])
            chat_message_list.append(chat_message)
    else:
        logger.info('No chat message yet.')

    return chat_message_list


def job():
    global current_month
    global current_year
    global merchant_name

    current_date = datetime.now().date()
    current_month = datetime.now().month
    current_year = datetime.now().year

    # if str(current_date.day) == "1":
    message_history_list = get_chat_message_history(month=current_month, year=current_year)

    if message_history_list:
        merchant_name = message_history_list[0].name
        results = preprocessing.cleaning(message_history_list)
        for result in results:
            print(result.content)


if __name__ == '__main__':
    init_logger()
    # schedule.every().day.at("02:00").do(job)
    # schedule.every(5).seconds.do(job)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
