import logging

import pandas

from model.chat_message import ChatMessage
from repository.database.data_manager import DataManager

logger = logging.getLogger("goliath")

class Repository(object):

    # def __init__(self):
    #     # init DataManager
    #     self.data_manager = DataManager()
    #     self.data_manager.create_database()
    #     self.data_manager.create_tables()
    #
    # def insert_into_online_shop(self, topic_cluster, word, score, merchant_name, year, month):
    #     self.data_manager.insert_into_online_shop(topic_cluster=topic_cluster,
    #                                               word=word,
    #                                               score=score,
    #                                               merchant_name=merchant_name,
    #                                               year=year,
    #                                               month=month)

    @staticmethod
    def get_chat_message_history(month, year):
        """
        Get chat history based on year and month.

        :param month: month. example value 8.
        :param year: year. example value 2018.
        :return: list of ChatMessage.
        """
        # chat_message_list_raw = pandas.read_csv(f'./resource/dataset/{month}_{year}.csv', sep=',')
        chat_message_list_raw = pandas.read_csv(f'./resource/dataset/11_2017.csv', sep=',')
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

    @staticmethod
    def get_slang_word():
        return pandas.read_csv('resource/slang_word_list.csv', sep=',', header=None)
