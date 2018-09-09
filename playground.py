import logging
import sys
from multiprocessing import cpu_count
import pandas
from gensim.corpora import Dictionary, MmCorpus
from gensim.models import TfidfModel, LdaMulticore, CoherenceModel
import csv
from gensim import models
import pyLDAvis.gensim

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# init Logger
logger = logging.getLogger("goliath")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logfile_handler = logging.StreamHandler(stream=sys.stdout)
logfile_handler.setFormatter(formatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(logfile_handler)

if __name__ == '__main__':
    documents_list = pandas.read_csv("2018_clean.txt", header=None).values
    documents = []
    for doc in documents_list:
        documents.append(str(doc[0]))
    documents = [result.split() for result in documents]

    dictionary = Dictionary(documents)

    # build bag of words
    bow_corpus = [dictionary.doc2bow(document) for document in documents]

    ldaa = models.LdaModel.load('lda_model.model')
    data = pyLDAvis.gensim.prepare(ldaa, bow_corpus, dictionary)
    pyLDAvis.display(data)
    pyLDAvis.save_html(data, 'topic_modeling.html')

    # calculate tf idf
    # tf_idf = TfidfModel(bow_corpus)
    # corpus_tf_idf = tf_idf[bow_corpus]

    # find highest coherence score
    # lda_models_with_coherence_score = {}
    # with open("coherence_history.csv", "w", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["score", "num_topic"])
    #     for index in range(2, 22, 2):
    #         lda_model = LdaMulticore(corpus_tf_idf,
    #                                  num_topics=index,
    #                                  id2word=dictionary,
    #                                  passes=2,
    #                                  workers=cpu_count())
    #
    #         coherence_model_lda = CoherenceModel(model=lda_model,
    #                                              texts=documents,
    #                                              corpus=bow_corpus,
    #                                               coherence='c_v')
    #         coherence_score = coherence_model_lda.get_coherence()
    #         lda_models_with_coherence_score[coherence_score] = lda_model
    #         writer.writerow([coherence_score, index])
    #         logger.info(f'Coherence score: {coherence_score}')
    #
    # # running the best lda model based on highest coherence score
    # lda_model = lda_models_with_coherence_score[max(lda_models_with_coherence_score)]
    # lda_model.save("lda_model.model")
    # model = models.LdaModel.load('lda_model.model')
    #
    # with open("lda_model_raw.csv", "w", newline="") as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["cluster", "word", "score"])
    #     for cluster, topic_term in model.show_topics(-1, num_words=100, formatted=False):
    #         for topic in topic_term:
    #             writer.writerow([cluster + 1, topic[0], topic[1]])
    #             logger.info(
    #                 f'Topic Cluster: {cluster + 1}, '
    #                 f'Word: {topic[0]}, '
    #                 f'Score: {topic[1]}, '
    #             )
