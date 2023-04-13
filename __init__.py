import configparser
import csv
import inspect
import itertools
import json
import datetime
import logging
import pathlib
from collections import defaultdict
from functools import lru_cache
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
        file_path = PROJECT_PATH / 'neptunia/data/cache.csv'
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            map_to_csv = map(lambda x: [x], self.get(key))
            csv_writer.writerows(map_to_csv)


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
    middleware_responses = defaultdict(list)

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
            # Persist the results of each middleware on the
            # main Middleware parent class
            self.middleware_responses[klass.verbose_name] = klass.container


class File:
    def __init__(self, path, name=None):
        self.path = path
        self.name = name or path.stem

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.path})>'

    def __hash__(self):
        return hash((self.name, str(self.path)))

    def __str__(self):
        return str(self.read())

    def __eq__(self, name):
        return any([
            self.name == name,
            name in self.name
        ])

    def __iter__(self):
        for value in self.read():
            yield value

    @property
    def is_csv(self):
        return 'csv' in self.path.name

    @property
    def is_json(self):
        return 'json' in self.path.name

    def iter_chunks(self, chunks=10):
        """Returns a group of iterators sliced by `n`
        number of items"""
        if chunks < 1:
            raise ValueError('Chunks should be at least 1')
        iterable = iter(self.read())
        while True:
            chunked_items = itertools.islice(iterable, chunks)
            try:
                first_element = next(chunked_items)
            except StopIteration:
                return
            yield itertools.chain([first_element], chunked_items)

    @lru_cache(maxsize=1)
    def read(self):
        """Reads the content a file"""
        with open(self.path, encoding='utf-8') as f:
            if self.is_csv:
                reader = csv.reader(f)
                data = itertools.chain(*list(reader))
                return set(data)
            elif self.is_json:
                return json.load(f)
            else:
                return f.read()

    def write(self, values):
        with open(self.path, mode='+a', newline='', encoding='utf-8') as f:
            if f.writable():
                if self.is_csv:
                    writer = csv.writer(f)
                    for value in values:
                        writer.writerow(value)
                elif self.is_json:
                    data = json.load(f)
                    data['date'] = str(datetime.datetime.now().timestamp())
                    data['cache'] = json.dumps(values)
                    json.dump(data, f)
                else:
                    f.write(values)


class Storage:
    """A class that preload files from
    the storage container"""
    _files_cache = []
    file_map = {}

    def __init__(self):
        self._files_cache = self.load_files()
        for file in self._files_cache:
            self.file_map[file.stem] = File(file)
        logger.instance.info(f'Storage loaded: {len(self)} files')

    def __repr__(self):
        return f'<{self.__class__.__name__} files: {self.__len__()}>'

    def __getitem__(self, name):
        return self.get(name)

    def __contains__(self, name):
        return self.has_file(name)

    def __len__(self):
        return len(self._files_cache)

    def load_files(self):
        return list(pathlib.Path('neptunia/data').glob('**/*'))

    def has_file(self, name):
        items = list(filter(lambda x: name in x.name, self._files_cache))
        if items:
            return True
        return False

    def get(self, name):
        return self.file_map[name]


cache = Cache()
middlewares = Middlewares()
storage = Storage()

cache.set('config', config)
cache.set('middlewares', middlewares)
cache.set('project_path', PROJECT_PATH)
cache.set('storage', storage)
