import logging
import sys
import schedule
from datetime import datetime
from multiprocessing import cpu_count

import pandas
from gensim.corpora import Dictionary, MmCorpus
from gensim.models import TfidfModel, LdaMulticore, CoherenceModel, LdaModel

from model.chat_message import ChatMessage
from preprocessing.preprocessing import Preprocessing
from utils.constant import NUM_TOPICS
from database.data_manager import DataManager
from settings.env_config import set_default_config

import pyLDAvis.gensim
import time
import matplotlib.pyplot as plt
import warnings
import csv

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

set_default_config()

# init Logger
logger = logging.getLogger("goliath")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logfile_handler = logging.StreamHandler(stream=sys.stdout)
logfile_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(logfile_handler)

# init our Preprocessing
preprocessing = Preprocessing(logger)


# init DataManager
# data_manager = DataManager(logger)
# data_manager.create_database()
# data_manager.create_tables()


def get_chat_message_history(month, year):
    """
    Get chat history based on year and month.

    :param month: month. example value 8.
    :param year: year. example value 2018.
    :return: list of ChatMessage.
    """
    # chat_message_list_raw = pandas.read_csv(f'./resource/dataset/{month}_{year}.csv', sep=',')
    chat_message_list_raw = pandas.read_csv(f'./resource/example/example_s.csv', sep=',')
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
    """ Function to be scheduling. """
    merchant_name = ""
    current_date = datetime.now().date()
    current_month = 12  # datetime.now().month
    current_year = 2019  # datetime.now().year
    worker = cpu_count() - 1

    # if str(current_date.day) == "1":
    message_history_list = get_chat_message_history(month=current_month, year=current_year)

    if message_history_list:
        merchant_name = message_history_list[0].name

        # cleaning chat text
        results = preprocessing.cleaning(message_history_list)
        logger.info(f'Preprocessing result size: {len(results)}')

        # build documents
        documents = [result.content.split() for result in results]
        dictionary = Dictionary(documents)
        logger.info(f'Preprocessing unique tokens: {len(dictionary)}')

        # TODO save dict into file (just for testing)
        dictionary.save(f'{current_month}-{current_year}-dictionary.dict')

        # build bag of words
        bow_corpus = [dictionary.doc2bow(document) for document in documents]

        # TODO save bag of words corpus into file (just for testing)
        MmCorpus.serialize(f'{current_month}-{current_year}-corpus.mm', bow_corpus)

        # calculate tf idf
        tf_idf = TfidfModel(bow_corpus)
        corpus_tf_idf = tf_idf[bow_corpus]

        # find highest coherence score
        lda_models_with_coherence_score = {}
        coherence_scores = []
        start_time = time.time()
        for index in range(2, NUM_TOPICS + 1):
            lda_model = LdaMulticore(corpus=corpus_tf_idf,
                                     num_topics=index,
                                     id2word=dictionary,
                                     alpha='asymmetric',
                                     eta='symmetric',
                                     workers=worker)

            coherence_model_lda = CoherenceModel(model=lda_model,
                                                 texts=documents,
                                                 corpus=corpus_tf_idf,
                                                 coherence='c_v')
            coherence_score = coherence_model_lda.get_coherence()
            lda_models_with_coherence_score[coherence_score] = lda_model
            coherence_scores.append(coherence_score)
            logger.info(f'Coherence score: {coherence_score}')

        # running the best lda model based on highest coherence score
        lda_model = lda_models_with_coherence_score[max(lda_models_with_coherence_score)]

        with open(f'{current_month}-{current_year}-executions_info.csv', "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["cpu_count", "num_tokens", "time", "num_topics"])
            writer.writerow([worker, len(dictionary), time.time() - start_time, NUM_TOPICS])

        rangex = range(2, NUM_TOPICS + 1)
        plt.plot(rangex, coherence_scores)
        plt.xlabel("Num Topics")
        plt.ylabel("Coherence score")
        plt.legend("coherence_scores", loc='best')
        plt.savefig(f'{current_month}-{current_year}-coherence-scores')

        # TODO save lda model into file (just for testing)
        lda_model.save(f'{current_month}-{current_year}-lda-model.mm')
        data = pyLDAvis.gensim.prepare(LdaModel.load(f'{current_month}-{current_year}-lda-model.mm'),
                                       MmCorpus(f'{current_month}-{current_year}-corpus.mm'),
                                       Dictionary.load(f'{current_month}-{current_year}-dictionary.dict'))
        pyLDAvis.display(data)
        pyLDAvis.save_html(data, f'{current_month}-{current_year}-visual.html')

        # save into DB
        for cluster, topic_term in lda_model.show_topics(-1, num_words=20, formatted=False):
            for topic in topic_term:
                logger.info(
                    f'Topic Cluster: {cluster + 1}, '
                    f'Word: {topic[0]}, '
                    f'Score: {topic[1]}, '
                    f'Merchant: {merchant_name}, '
                    f'Year: {current_year}, '
                    f'Month: {current_month}'
                )
                # data_manager.insert_into_online_shop(topic_cluster=cluster + 1,
                #                                      word=topic[0],
                #                                      score=topic[1],
                #                                      merchant_name=merchant_name,
                #                                      year=current_year,
                #                                      month=current_month)


if __name__ == '__main__':
    # schedule.every().day.at("02:00").do(job)
    # schedule.every(5).seconds.do(job)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
