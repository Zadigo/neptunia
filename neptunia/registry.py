from neptunia import PROJECT_PATH, Cache, Config, Middlewares, Storage
from neptunia.app import main, main_from_xml

CONFIG = Config()
CACHE = Cache()
STORAGE = Storage()

CACHE.set('config', CONFIG)
CACHE.set('project_path', PROJECT_PATH)
CACHE.set('storage', STORAGE)


class AppRegistry:
    """Loads all the required applications
    for running the web scrapper"""

    cache = CACHE
    middleware_class = Middlewares

    def __init__(self):
        self.middlewares = None
        self.app_config = None
        self.storage = None
        self.is_ready = False

    def __call__(self, initial_cache={}, *args, **kwargs):
        self.load(initial_cache=initial_cache)
        return self
    
    def __repr__(self) -> str:
        return f'AppRegistr(is_ready={self.is_ready})'

    def configure_cache(self, **kwargs):
        kwargs.update({'registry': self})
        self.cache.bulk_set(**kwargs)

    def load(self, initial_cache={}):
        middlewares = self.middleware_class()
        self.middlewares = middlewares

        self.app_config = CONFIG
        self.storage = STORAGE

        self.configure_cache(**initial_cache)

        self.is_ready = True

    def run_scrapper(self, start_url=None, start_urls=[], xml_page=False, **kwargs):
        if not self.is_ready:
            raise ValueError("Registry is not ready")
        
        if not xml_page:
            main(start_urls=start_urls)
        else:
            if start_url is None:
                raise
            main_from_xml(start_url)


registry = AppRegistry()
