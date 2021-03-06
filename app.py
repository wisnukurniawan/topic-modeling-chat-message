import logging
import sys
import schedule
import time
import calendar
from datetime import datetime

from gensim.corpora import Dictionary
from gensim.models import TfidfModel, LdaModel, CoherenceModel

from preprocessing.preprocessing import Preprocessing
from utils.constant import NUM_TOPICS
from settings.env_config import set_default_config
from repository.repository import Repository

set_default_config()

# init Logger
logger = logging.getLogger("goliath")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logfile_handler = logging.StreamHandler(stream=sys.stdout)
logfile_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(logfile_handler)

# init our Preprocessing
preprocessing = Preprocessing()

# init our Repository
repository = Repository()


def job():
    """ Function to be scheduling. """
    current_month = 3  # datetime.now().month
    current_year = 2017  # datetime.now().year

    # if is_last_month(current_year, current_month):
    message_history_list = Repository.get_chat_message_history(month=current_month, year=current_year)

    if message_history_list:
        merchant_name = message_history_list[0].name

        # cleaning chat text
        results = preprocessing.cleaning(message_history_list)
        logger.info(f'Preprocessing result {len(results)} items')

        # build documents
        documents = [result.content.split() for result in results]
        documents = Preprocessing.identify_phrase(documents)
        dictionary = Dictionary(documents)
        logger.info(f'Preprocessing unique tokens: {len(dictionary)}')

        # build bag of words
        bow_corpus = [dictionary.doc2bow(document) for document in documents]

        # calculate tf idf
        tf_idf = TfidfModel(bow_corpus)
        corpus_tf_idf = tf_idf[bow_corpus]

        # find highest coherence score
        lda_models_with_coherence_score = {}
        for index in range(1, NUM_TOPICS + 1):
            lda_model = LdaModel(corpus=corpus_tf_idf,
                                 num_topics=index,
                                 id2word=dictionary)

            coherence_model_lda = CoherenceModel(model=lda_model,
                                                 texts=documents,
                                                 corpus=corpus_tf_idf,
                                                 coherence='c_v')
            coherence_score = coherence_model_lda.get_coherence()
            lda_models_with_coherence_score[coherence_score] = lda_model
            logger.info(f'Coherence score: {coherence_score}')

        # running the best lda model based on highest coherence score
        lda_model = lda_models_with_coherence_score[max(lda_models_with_coherence_score)]

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
                repository.insert_into_online_shop(topic_cluster=cluster + 1,
                                                   word=topic[0],
                                                   score=topic[1],
                                                   merchant_name=merchant_name,
                                                   year=current_year,
                                                   month=current_month)


def func_test():
    logger.info("HELLO WORLD!")


def is_last_month(current_year, current_month):
    calendar_range = calendar.monthrange(current_year, current_month)

    last_date_in_month = calendar_range[1]
    current_date = datetime.now().date().day
    return last_date_in_month == current_date


if __name__ == '__main__':
    # schedule.every().day.at("02:00").do(job)
    # schedule.every(5).seconds.do(job)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
