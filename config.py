import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIGRATIONS_DIR = 'uricomcuscuz/migrations'

    UNIVERSITY = os.environ['UNIVERSITY']
    # o número de páginas na universidade `?page={}`
    UNIVERSITY_TOTAL_PAGES = os.environ['UNIVERSITY_TOTAL_PAGES']

    # número de submissões exibidas por página
    PAGINATION = 30


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
