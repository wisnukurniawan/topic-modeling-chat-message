import logging
import sys
import schedule
from datetime import datetime
from multiprocessing import cpu_count

import pandas
from gensim.corpora import Dictionary
from gensim.models import TfidfModel, LdaMulticore, CoherenceModel

from model.chat_message import ChatMessage
from preprocessing.preprocessing import Preprocessing
from utils.constant import NUM_TOPICS

# init logger
logger = logging.getLogger("goliath")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logfile_handler = logging.StreamHandler(stream=sys.stdout)
logfile_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(logfile_handler)

# init our Preprocessing
preprocessing = Preprocessing(logger)

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

        # cleaning chat text
        results = preprocessing.cleaning(message_history_list)

        # build documents
        documents = []
        for result in results:
            documents.append(result.content.split())
        dictionary = Dictionary(documents)

        # build bag of words
        bow_corpus = [dictionary.doc2bow(document) for document in documents]

        # calculate tfidf
        tfidf = TfidfModel(bow_corpus)
        corpus_tfidf = tfidf[bow_corpus]

        # find highest coherence score
        lda_models_with_coherence_score = {}
        for num_topic in range(NUM_TOPICS):
            lda_model = LdaMulticore(corpus_tfidf,
                                     num_topics=num_topic + 1,
                                     id2word=dictionary,
                                     passes=2,
                                     workers=cpu_count())

            coherence_model_lda = CoherenceModel(model=lda_model,
                                                 texts=documents,
                                                 corpus=bow_corpus,
                                                 coherence='c_v')
            coherence_score = coherence_model_lda.get_coherence()
            lda_models_with_coherence_score[coherence_score] = lda_model
            logger.info(f'Coherence score: {coherence_score}')

        # running the best lda model based on highest coherence score
        lda_model = lda_models_with_coherence_score[max(lda_models_with_coherence_score)]
        topic_terms = []
        for topic in lda_model.print_topics(-1):
            lda_model_topic_terms_dict = {}
            for k, v in lda_model.get_topic_terms(topic[0]):
                lda_model_topic_terms_dict[dictionary[k]] = v
            topic_terms.append(lda_model_topic_terms_dict)

        # save into DB
        for index, topic_term in enumerate(topic_terms):
            for k, v in topic_term.items():
                print('Index: {} Word: {} Frekuensi: {}'.format(index + 1, k, v))


if __name__ == '__main__':
    # schedule.every().day.at("02:00").do(job)
    # schedule.every(5).seconds.do(job)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
