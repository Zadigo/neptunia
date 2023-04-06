import configparser
import csv
import inspect
import json
import logging
import pathlib
from collections import defaultdict
from importlib import import_module

PROJECT_PATH = pathlib.Path('.').absolute()


class Logger:
    instance = None

    def __init__(self, name='MAIN'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        logger.addHandler(handler)

        log_format = logging.Formatter(
            '%(asctime)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d'
        )
        handler.setFormatter(log_format)
        self.instance = logger


logger = Logger()


class Cache:
    configuration = None
    container = defaultdict(list)

    def __init__(self):
        logger.instance.info('Cache loaded')

    def __str__(self):
        return str(self.container)

    def __len__(self):
        keys = self.container.keys()
        return sum([self.container[x] for x in keys])

    def __getitem__(self, key):
        return self.container[key]

    def set(self, key, value):
        if isinstance(value, list):
            self.container[key].extend(value)
        else:
            self.container[key].append(value)

    def get(self, key):
        return self.container[key]

    def reset_key(self, key):
        self.container[key] = []

    def persist(self, key):
        """Persist the data of a given key
        to the "cache.csv" file"""
        file_path = PROJECT_PATH / 'neptunia/cache.csv'
        with open(file_path, mode='w', newline='\n', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            map_fo_csv = map(lambda x: [x], self.get(key))
            csv_writer.writerows(map_fo_csv)


cache = Cache()


class Config:
    def __init__(self):
        instance = configparser.ConfigParser()
        with open(PROJECT_PATH / 'neptunia/conf.cfg', mode='r') as f:
            instance.read_file(f)
            self.settings = instance
        logger.instance.info('Configuration file loaded')

    def __repr__(self):
        return f'<{self.__class__.__name__}[sections={self.settings.sections()}]>'

    def __getattr__(self, name):
        value = getattr(self.settings, name, None)
        if value is None:
            raise AttributeError('Attribute does not exist')
        return value

    def load_as_array(self, section, name):
        result = self.settings.get(section, name)
        return json.loads(result)


config = Config()


class Middlewares:
    """Actions to after the response
    has been completed by the crawler"""
    container = {}
    MODULE = None

    def __init__(self):
        self.MODULE = import_module('neptunia.neptunia.middlewares')
        self._middleware_cache = config.load_as_array('options', 'middlewares')
        registered_middlewares = map(
            lambda x: x.rsplit('.', maxsplit=1),
            self._middleware_cache
        )
        klasses = inspect.getmembers(self.MODULE, inspect.isclass)
        for registered_middleware in registered_middlewares:
            name = registered_middleware[-1]
            for klass in klasses:
                if name not in klass:
                    continue
                self.container[name] = klass[-1]()
        names = ', '.join(self.container.keys())
        logger.instance.info(f"Middlewares loaded: {names}")

    def __repr__(self):
        return f'<{self.__class__.__name__}[count={self.__len__()}]>'

    def __len__(self):
        return len(self.container)

    def __getitem__(self, name):
        return self.container[name]

    def run_middlewares(self, response, soup, xml):
        for klass in self.container.values():
            klass(response, soup, xml)


middlewares = Middlewares()

connections = Connections()

cache.set('config', config)
cache.set('middlewares', middlewares)
cache.set('project_path', PROJECT_PATH)
cache.set('connections', connections)
