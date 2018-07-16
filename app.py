import logging
import sys
import schedule
import time
from datetime import datetime
from multiprocessing import cpu_count

import pandas
from flashtext.keyword import KeywordProcessor
from spacy.lang.id import Indonesian

from model.chat_message import ChatMessage
from preprocessing.utils import PreprocessingUtils, PreprocessingUtilsV2
from utils import constant

# init NLP
nlp = Indonesian()

# init flash text
# build slang word corpus
keyword_processor_slang_word = KeywordProcessor()
slang_words_raw = pandas.read_csv('resource/slang_word_list.csv', sep=',')
for word in slang_words_raw.values:
    keyword_processor_slang_word.add_keyword(word[0], word[1])

# build emoticon corpus
keyword_processor_emoticon = KeywordProcessor()
emoticon_raw = constant.EMOTICON_LIST
for key, values in emoticon_raw:
    for value in values:
        keyword_processor_emoticon.add_keyword(value, key)

# init logger
logger = logging.getLogger("goliath")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logfile_handler = logging.StreamHandler(stream=sys.stdout)
logfile_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(logfile_handler)

merchant_name = ""
current_month = ""
current_year = ""


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


def cleaning(chat_message_list):
    """
    Pre-processing the content from ChatMessage.

    :param chat_message_list: dirty content from list of ChatMessage.
    :return: observable list of ChatMessage.
    """
    chat_message_list_temp = []

    if chat_message_list:
        logger.info('Pre-processing started...')
        start_time = time.time()

        for chat_message in chat_message_list:
            content = preprocessing_flow(chat_message.content)
            chat_message.content = content
            if content.strip():
                chat_message_list_temp.append(chat_message)

        logger.info(f'Pre-processing finished. {time.time() - start_time} seconds')
    else:
        logger.info('No chat message yet.')

    return chat_message_list_temp


def cleaning_with_pipe(chat_message_list):
    """
    [DEPRECATED]
    Pre-processing the content from ChatMessage with multi threading from spaCy.

    :param chat_message_list: dirty content from list of ChatMessage.
    :return: observable list of ChatMessage.
    """

    if chat_message_list:
        logger.info('Pre-processing started...')
        start_time = time.time()
        chat_content_list = []
        index = 0

        for chat_message in chat_message_list:
            chat_content_list.append(chat_message.content)

        for content in nlp.pipe(chat_content_list, n_threads=cpu_count()):
            chat_message_list[index].content = preprocessing_flow(content.text)
            index = index + 1

        logger.info(f'Pre-processing finished. {time.time() - start_time} seconds')
    else:
        logger.info('No chat message yet.')

    return chat_message_list


def preprocessing_flow(content):
    """
    Preprocessing flow.
    """
    content = PreprocessingUtilsV2.normalize_emoticon(content, keyword_processor_emoticon)  # normalize emoticon
    content = PreprocessingUtils.normalize_url(content)  # normalize url
    content = PreprocessingUtils.remove_url(content)  # remove url
    content = PreprocessingUtils.remove_email(content)  # remove email
    content = PreprocessingUtils.remove_digit_number(content)  # remove digit number
    content = PreprocessingUtils.case_folding_lowercase(content)  # case folding lower case
    content = PreprocessingUtils.remove_punctuation(content)  # remove punctuation
    content = PreprocessingUtilsV2.normalize_slang_word(content, keyword_processor_slang_word)  # normalize slang word
    content = PreprocessingUtils.remove_unused_character(content)  # remove unused character
    content = PreprocessingUtils.stemming_tokenize_and_remove_stop_word(content, nlp)  # stemming, tokenize, remove stop word
    content = PreprocessingUtils.join_negation(content)  # join negation word
    content = PreprocessingUtils.removing_extra_space(content)  # remove extra space between word

    # TODO add another pre-processing if needed

    return content


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
        results = cleaning(message_history_list)
        # for result in results:
        #     print(result)


if __name__ == '__main__':
    # schedule.every().day.at("02:00").do(job)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
