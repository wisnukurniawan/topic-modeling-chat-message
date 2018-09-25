import logging
import sys
import schedule
import time
import calendar
import csv
from datetime import datetime
from multiprocessing import cpu_count

from gensim.corpora import Dictionary, MmCorpus
from gensim.models import TfidfModel, LdaMulticore, CoherenceModel, LdaModel

from preprocessing.preprocessing import Preprocessing
from utils.constant import NUM_TOPICS
from settings.env_config import set_default_config
from repository.repository import Repository
import matplotlib.pyplot as plt
import pyLDAvis.gensim
import warnings

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
preprocessing = Preprocessing()

# init our Repository
repository = Repository()


def job():
    """ Function to be scheduling. """
    current_month = 12  # datetime.now().month
    current_year = 2017  # datetime.now().year

    worker = cpu_count() - 1

    # if is_last_month(current_year, current_month):
    message_history_list = Repository.get_chat_message_history(month=current_month, year=current_year)

    if message_history_list:
        merchant_name = message_history_list[0].name
        raw_data_size = len(message_history_list)
        logger.info(f'Size {raw_data_size} items')

        # cleaning chat text
        start_time_preprocessing = time.time()
        results = preprocessing.cleaning(message_history_list)
        logger.info(f'Preprocessing result {len(results)} items')
        end_time_preprocessing = time.time() - start_time_preprocessing
        result_size_prep = len(results)

        # build documents
        documents = [result.content.split() for result in results]
        documents = Preprocessing.identify_phrase(documents)
        dictionary = Dictionary(documents)

        # TODO (just for testing)
        dictionary.save(f'{current_month}-{current_year}-dictionary.dict')

        logger.info(f'Preprocessing unique tokens: {len(dictionary)}')

        # build bag of words
        bow_corpus = [dictionary.doc2bow(document) for document in documents]

        # TODO (just for testing)
        MmCorpus.serialize(f'{current_month}-{current_year}-corpus.mm', bow_corpus)

        # calculate tf idf
        tf_idf = TfidfModel(bow_corpus)
        corpus_tf_idf = tf_idf[bow_corpus]

        # find highest coherence score
        lda_models_with_coherence_score = {}
        coherence_scores = []
        start_time_training = time.time()
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
            coherence_scores.append(coherence_score)
            logger.info(f'Coherence score: {coherence_score}')

        # running the best lda model based on highest coherence score
        lda_model = lda_models_with_coherence_score[max(lda_models_with_coherence_score)]

        # TODO (just for testing)
        with open(f'{current_month}-{current_year}-executions_info.csv', "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["raw_data_size", "preprocessing_time", "clean_data_size", "cpu_count", "num_tokens", "training_time",
                 "num_topics"])
            writer.writerow([raw_data_size, end_time_preprocessing, result_size_prep, worker, len(dictionary),
                             time.time() - start_time_training, NUM_TOPICS])

        # TODO (just for testing)
        rangex = range(1, NUM_TOPICS + 1)
        plt.plot(rangex, coherence_scores)
        plt.xlabel("Num Topics")
        plt.ylabel("Coherence score")
        plt.legend("coherence_scores", loc='best')
        plt.savefig(f'{current_month}-{current_year}-coherence-scores')

        # TODO (just for testing)
        lda_model.save(f'{current_month}-{current_year}-lda-model.mm')
        if max(coherence_scores) != coherence_scores[0]:
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
                repository.insert_into_online_shop(topic_cluster=cluster + 1,
                                                   word=topic[0],
                                                   score=topic[1],
                                                   merchant_name=merchant_name,
                                                   year=current_year,
                                                   month=current_month)


def is_last_month(current_year, current_month):
    calendar_range = calendar.monthrange(current_year, current_month)

    last_date_in_month = calendar_range[1]
    current_date = datetime.now().date().day
    return last_date_in_month == current_date


if __name__ == '__main__':
    # schedule.every().day.at("02:00").do(test)
    # schedule.every(5).seconds.do(test)
    job()

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
