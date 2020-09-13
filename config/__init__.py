import logging
import os
from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Cfg(object, metaclass=Singleton):

    def __init__(self, stage):
        self.stage = stage
        configp = ConfigParser()
        errors_logger = logging.getLogger("movies.errors")
        logging.getLogger().setLevel(logging.INFO)
        errors_logger.addHandler(logging.StreamHandler())
        configp.read("config/" + stage + ".ini")
        self.Config = configp.get
        self.Logger = errors_logger
        self.debug = self.Config('log', 'debug')
        db_url = self.Config('database', 'url')
        try:
            self.engine = create_engine(db_url, pool_recycle=1, echo=True)
            self.DB = sessionmaker(bind=self.engine)
        except Exception as e:
            self.Logger.error(e)
