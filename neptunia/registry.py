class AppRegistry:
    """Loads all the required applications
    for running the web scrapper"""

    def __init__(self):
        self.cache = None
        self.middlewares = None
        self.app_config = None
        self.storage = None
        self.is_ready = False

    def configure_cache(self):
        # TODO: Load the registry in the
        # current application cache
        pass

    def load(self):
        self.is_ready = True

    def run_scrapper(self, url, **kwargs):
        if not self.is_ready:
            raise ValueError("Registry is not ready")


registry = AppRegistry()
