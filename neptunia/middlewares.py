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


class SEOMiddleware(BaseMiddleware):
    """Middleware that runs an SEO audit on
    all the visited pages"""

    audits = deque()
    failed_urls = []
    csv_file = [['title', 'title_length', 'title_is_valid', 'description',
                    'description_is_valid', 'url', 'word_analysis', 'status_code']]

    def __call__(self, response, soup, xml):
        if 400 >= response.status_code <= 599:
            self.failed_urls.append({
                'url': response.url,
                'status_code': response.status_code
            })
        else:
            title = soup.find('title').text

            instance = NLTKWordTokenizer()
            tokens = instance.tokenize(soup.body.text)
            counter = Counter(tokens)
            most_common = counter.most_common(10)

            description = soup.find('meta', attrs={'name': 'description'}).text
            description_tokens = instance.tokenize(description)


            audit = {
                'title': title,
                'title_length': len(title),
                'title_is_valid': len(title) <= 60,
                'description': description,
                'description_is_valid': len(description) <= 150,
                'url': response.url,
                'word_analysis': most_common,
                'status_code': response.status_code
            }
            self.csv_file.append([
                title,
                len(title),
                len(title) <= 60,
                description,
                len(description) <= 150,
                response.url,
                most_common,
                response.status_code
            ])
            self.audits.append(audit)

    @property
    def get_report(self):
        return {
            'audit': self.audits,
            'errors': self.failed_urls
        }
