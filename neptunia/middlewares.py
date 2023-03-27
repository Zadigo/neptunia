import re
from collections import Counter, deque

from nltk.tokenize import NLTKWordTokenizer

from neptunia import logger


class BaseMiddleware:
    """Use middlewares to run specific functionnalities
    after the page has been retrieved"""
    container = {}

    def __call__(self, response, soup, xml):
        pass


class TextMixin:
    def get_text(self, soup):
        instance = NLTKWordTokenizer()
        return instance.tokenize(soup.text)


class TextMiddleware(TextMixin, BaseMiddleware):
    """Collects the text on all the visited pages"""

    def __call__(self, response, soup, xml):
        words = self.get_text(soup)
        self.container[response.url] = words
        logger.instance.info(f'Found {len(words)} words')


class EmailMiddleware(TextMixin, BaseMiddleware):
    """Collects emails on all visited pages"""
    container = set()

    def __call__(self, response, soup, xml):
        def identify_email(value):
            result = re.match(r'^(?P<user>.*)\@(?P<domain>.*)$', value)
            if result:
                return result.group()

        emails = map(identify_email, self.get_text(soup))
        emails_found = set(list(emails))
        # Remove all None values from the dataset
        valid_items = list(filter(lambda x: x is not None, emails_found))
        self.container = self.container.union(valid_items)

        logger.instance.info(f"Found {len(valid_items)} email(s)")


class ImageMiddleware(BaseMiddleware):
    """Collect images on all visited pages"""
    container = deque()
    restricted_to = ['jpg', 'jpeg']

    def __call__(self, response, soup, xml):
        urls = soup.find_all('a')

        def identify_image(value):
            if '.' in value:
                _, extension = value.rsplit('.', maxsplit=1)
                if extension in self.restricted_to:
                    return True
                return False
            return False
        valid_images = filter(identify_image, urls)
        self.container.extendleft(list(valid_images))
