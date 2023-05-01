import re
from collections import Counter, OrderedDict, deque

from nltk.tokenize import LineTokenizer, NLTKWordTokenizer
from sklearn.feature_extraction.text import CountVectorizer

from neptunia import logger


class BaseMiddleware:
    """Use middlewares to run specific functionnalities
    after the page has been retrieved"""
    container = {}

    def __init__(self):
        self.verbose_name = self.__class__.__name__
        
    def __call__(self, response, soup, xml):
        pass

    def get_container(self):
        to_list = ['set', 'deque']
        if type(self.container).__name__ in to_list:
            return list(self.container)
        return self.container


class TextMixin:
    tokenizer_class = NLTKWordTokenizer

    def get_text(self, soup):
        """Returns the text element from a document"""
        try:
            text = soup.text
        except:
            logger.instance.error('Text not found in HTML page')
            return []
        else:
            return self.tokenize(text)

    def tokenize(self, text):
        instance = self.tokenizer_class()
        return instance.tokenize(text)

    def get_vectorizer(self, language='en'):
        """Use sci-kit word vectorizer to check and remove
        stop words from the document"""
        from neptunia import storage
        filename = 'stop_words_french' if language == 'fr' else 'stop_words_english'
        text = storage.get_file_content(filename)

        tokenizer = LineTokenizer()
        french_stop_words = tokenizer.tokenize(text)

        return CountVectorizer(
            stop_words=french_stop_words,
            max_df=1.0
        )
    

class TextMiddleware(TextMixin, BaseMiddleware):
    """Collects the text on all the visited pages"""
    scrapped_words = set()

    def __call__(self, response, soup, xml):
        words = self.get_text(soup)

        vectorizer = self.get_vectorizer(words)
        vectorizer.fit_transform(words)
        vocabulary = vectorizer.vocabulary_

        self.scrapped_words = self.scrapped_words.union(set(words))
        self.container[response.url] = vocabulary
        logger.instance.info(f'Found {len(words)} words')


class EmailMiddleware(TextMixin, BaseMiddleware):
    """Collects emails on all visited pages"""

    container = set()

    def __call__(self, response, soup, xml):
        def validate_values(value):
            if value is None:
                return False

            result = re.match(r'^(?:mailto\:)?(.*\@.*)$', value)
            if result:
                return True

        def identify_email(value):
            if '@' in value:
                return value
            return None

        def parse_url(url):
            value = url.attrs.get('href', None)
            if value is not None and '@' in value:
                return value
            return None

        # 1. Get all possible emails from plain text
        emails_from_text = map(identify_email, self.get_text(soup))
        # 2. Get all possible emails from <a></a> tags
        emails_from_urls = map(parse_url, soup.find_all('a'))

        emails_from_text = set(list(emails_from_text))
        emails_from_urls = set(list(emails_from_urls))
        unvalidated_emails = emails_from_text.union(emails_from_urls)

        valid_items = list(filter(validate_values, unvalidated_emails))

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


class SEOMiddleware(TextMixin, BaseMiddleware):
    """Middleware that runs an SEO audit on
    all the visited pages"""

    container = deque()
    failed_urls = []
    csv_file = [['title', 'title_length', 'title_is_valid', 'description',
                 'description_is_valid', 'url', 'word_analysis', 'status_code']]

    def __call__(self, response, soup, xml):
        if 400 <= response.status_code <= 599:
            self.failed_urls.append({
                'url': response.url,
                'status_code': response.status_code
            })
        else:
            title = soup.find('title').text

            # instance = NLTKWordTokenizer()
            # tokens = instance.tokenize(soup.body.text)
            tokens = self.get_text(soup.body)
            counter = Counter(tokens)
            most_common = counter.most_common(10)

            description_object = soup.find(
                'meta',
                attrs={'name': 'description'}
            )

            try:
                description = description_object.attrs['content']
                description_text = description_object.text
            except:
                logger.instance.error('Could not find description text on page')
                self.container.append({})
            else:
                description_tokens = self.tokenize(description)

                audit = {
                    'title': title,
                    'title_length': len(title),
                    'title_is_valid': len(title) <= 60,
                    'description': description_text,
                    'description_is_valid': len(description_tokens) <= 150,
                    'url': response.url,
                    'word_analysis': dict(OrderedDict(most_common)),
                    'status_code': response.status_code
                }
                self.container.append(audit)

    @property
    def get_report(self):
        return {
            'audit': self.container,
            'errors': self.failed_urls
        }
