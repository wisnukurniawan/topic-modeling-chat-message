from os import environ


def set_default_config():
    # MySQL config
    environ.setdefault('MYSQL_USER', 'goliath')
    environ.setdefault('MYSQL_PASS', 'goliath')
    environ.setdefault('MYSQL_HOST', '127.0.0.1')
    environ.setdefault('MYSQL_DB', 'bi_online_shop')
    environ.setdefault('MYSQL_PORT', '3306')
