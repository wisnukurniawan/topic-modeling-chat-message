from os import environ
import uuid

import mysql.connector
from mysql.connector import errorcode

TABLES = {'online_shop': (
    "CREATE TABLE IF NOT EXISTS `online_shop` ("
    "  `id` varchar(36) NOT NULL,"
    "  `topic_cluster` int(11) DEFAULT NULL,"
    "  `word` varchar(255) DEFAULT NULL,"
    "  `score` float DEFAULT NULL,"
    "  `merchant_name` varchar(255) DEFAULT NULL,"
    "  `year` int(11) DEFAULT NULL,"
    "  `month` int(11) DEFAULT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")}


class DataManager(object):
    def __init__(self, logger):
        # init logger
        self.logger = logger

    @staticmethod
    def connector():
        """ Connect to MySQL database. """

        # init db connection
        config = {
            'user': environ.get('MYSQL_USER'),
            'password': environ.get('MYSQL_PASS'),
            'host': environ.get('MYSQL_HOST'),
            'database': environ.get('MYSQL_DB'),
            'raise_on_warnings': True,
            'use_pure': False,
        }
        connector = mysql.connector.connect(**config)
        return connector

    def create_database(self):
        connector = self.connector()
        cursor = connector.cursor()

        try:
            connector.database = environ.get('MYSQL_DB')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                try:
                    cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(environ.get('MYSQL_DB')))
                except mysql.connector.Error as err:
                    self.logger.info(f"Failed creating database: {err}")
                    exit(1)

                    connector.database = environ.get('MYSQL_DB')
            else:
                self.logger.info(err)
                exit(1)

        cursor.close()
        connector.close()

    def create_tables(self):
        connector = self.connector()
        cursor = connector.cursor()

        for name, ddl in TABLES.items():
            try:
                self.logger.info(f"Creating table: {name}")
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    self.logger.info("Already exists.")
                else:
                    self.logger.info(err.msg)
            else:
                self.logger.info("OK")

        cursor.close()
        connector.close()

    def insert_into_online_shop(self, topic_cluster, word, score, merchant_name, year, month):
        connector = self.connector()
        cursor = connector.cursor()

        add_data_query = ("INSERT INTO online_shop "
                          "(topic_cluster, word, score, merchant_name, year, month)"
                          "VALUES (%(topic_cluster)s, %(word)s, %(score)s, %(merchant_name)s, %(year)s, %(month)s)")

        data = {
            'id': str(uuid.uuid4()),
            'topic_cluster': topic_cluster,
            'word': word,
            'score': float(score),
            'merchant_name': merchant_name,
            'year': year,
            'month': month,
        }
        try:
            cursor.execute(add_data_query, data)
            connector.commit()
        except mysql.connector.Error:
            connector.rollback()

        cursor.close()
        connector.close()
