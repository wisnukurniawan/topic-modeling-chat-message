import re
from urllib.parse import urlparse

from utils import constant
from repository.repository import Repository


class PreprocessingUtils:
    @staticmethod
    def case_folding_lowercase(text):
        """
        Make all text lower case.

        :param text: (str) text to be lower.
        :return: (str) text has been lower case.
        """
        return text.lower()

    @staticmethod
    def normalize_emoticon(text):
        """
        Normalize the emoticon word.

        :param text: (str) text to be normalize.
        :return: (str) text has been normalize.
        """
        text_list = text.split(' ')
        emoticon_list = constant.EMOTICON_LIST

        for index in range(len(text_list)):
            for key, value in emoticon_list:
                if text_list[index] in value:
                    text_list[index] = key

        return ' '.join(text_list)

    @staticmethod
    def normalize_slang_word(text):
        """
        Normalize the slang/'alay' word.

        :param text: (str) text to be normalize.
        :return: (str) text has been normalize.
        """
        text_list = text.split(' ')
        slang_words_raw = Repository.get_slang_word()
        slang_word_dict = {}

        for item in slang_words_raw.values:
            slang_word_dict[item[0]] = item[1]

        for index in range(len(text_list)):
            if text_list[index] in slang_word_dict.keys():
                text_list[index] = slang_word_dict[text_list[index]]

        return ' '.join(text_list)

    @staticmethod
    def normalize_url(text):
        """
        Normalize url into product name based on merchant name

        :param text: (str) text to be normalize.
        :return: (str) text has been normalize.
        """
        text_list = text.split(' ')

        for index in range(len(text_list)):
            rgx = re.match("^https?://berrybenka.com", text_list[index])
            if rgx is not None:
                path = urlparse(text_list[index]).path
                path_list = path.split("/")
                if len(path_list) > 1:
                    if path_list[-2].isnumeric():
                        text_list[index] = path_list[-1].replace("-", constant.DELIMITER)

        return ' '.join(text_list)

    @staticmethod
    def remove_url(text):
        """ Remove url in text. """
        return re.sub(r'((http|https)://|www)[a-zA-Z0-9\-.]+\.[a-zA-Z]{2,3}(/\S*)?', '', text)

    @staticmethod
    def remove_unused_character(text):
        """ Remove characters that are less than two character. """
        text_list = text.split(' ')
        text_list_temp = []

        for index in range(len(text_list)):
            if len(text_list[index]) > 3:
                text_list_temp.append(text_list[index])

        return ' '.join(text_list_temp)

    @staticmethod
    def remove_email(text):
        """ Remove email in text. """
        return re.sub(
            r'[a-zA-Z0-9+._%\-]{1,256}@[a-zA-Z0-9][a-zA-Z0-9\-]{0,64}(\.[a-zA-Z0-9][a-zA-Z0-9\-]{0,25})+',
            '',
            text
        )

    @staticmethod
    def remove_punctuation(text):
        """ Remove all punctuation in text. """
        return re.sub(r'[^\s\w]', ' ', text)

    @staticmethod
    def remove_digit_number(text):
        """ Remove all digit number in text. """
        return re.sub(r'[^a-z ]*([.0-9])*\d', '', text)

    @staticmethod
    def join_negation(text):
        """  Join negation word with delimiter. """
        text_list = text.split(' ')

        for index in range(len(text_list)):
            if text_list[index] == constant.NEGATION_WORD:
                if index < len(text_list) - 1:
                    text_list[index] = text_list[index] + constant.DELIMITER + text_list[index + 1]
                    text_list[index + 1] = ''
                else:
                    text_list[index] = ''

        return ' '.join(text_list)

    @staticmethod
    def stemming_tokenize_and_remove_stop_word(text, nlp, stemmer):
        """ This func doing three process. It was stemming word, tokenize and then remove stop word. """
        text_list = []
        text_list_temp = []

        # stemming
        for token in nlp.tokenizer(text):
            token = str(token)
            if constant.DELIMITER not in token:
                text_list.append(stemmer.stem(token))
            else:
                text_list.append(token)

        # remove stop words
        for word in text_list:
            if not nlp.vocab[word].is_stop:
                text_list_temp.append(word)

        return ' '.join(text_list_temp)

    @staticmethod
    def remove_extra_space(text):
        """ Make extra space into one space. """
        text_list = text.split(' ')
        text_list_temp = []

        for word in text_list:
            if word.strip():
                text_list_temp.append(word.strip())

        return ' '.join(text_list_temp)

    @staticmethod
    def remove_repeated_character(text):
        """
        Remove repeated character more than two in text
        Why two not one character?
        Because some Indonesian word, there is like 'tunggu', 'saat', etc. We don't want remove it.
        """
        return re.sub(r'(.)\1{2,}', r'\1', text)



class PreprocessingUtilsV2:
    @staticmethod
    def normalize_emoticon(text, keyword_processor):
        """
        Normalize the emoticon word.

        :param keyword_processor: keyword_processor from flash text.
        :param text: text to be normalize.
        :return: text has been normalize.
        """
        return keyword_processor.replace_keywords(text)

    @staticmethod
    def normalize_slang_word(text, keyword_processor):
        """
        Normalize the slang/'alay' word use flash text.

        :param keyword_processor: keyword_processor from flash text.
        :param text: (str) text to be normalize.
        :return: (str) text has been normalize.
        """
        return keyword_processor.replace_keywords(text)
