import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATIONS_DIR = 'uricomcuscuz/migrations'
    # para converter os horários para hora local
    UTC = os.environ.get('UTC', -3)
    # o número de páginas na universidade `?page={}`
    TOTAL_PAGES = os.environ.get('TOTAL_PAGES', 1)
    # número de submissões por página
    SUBS_PER_PAGE = 30


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
