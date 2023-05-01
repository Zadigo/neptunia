import random
import time
from functools import lru_cache
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree

from neptunia import cache, logger, middlewares, storage
from neptunia.signals import Signal
from neptunia.utils import write_file

post_init = Signal()
address_visited = Signal()

MIDDLEWARES = 'neptune.middlewares'

WAIT_TIME = 35


@lru_cache(maxsize=300)
def get_random(func):
    values = func()
    if not values:
        return None
    return random.choice(list(values))


@get_random
def proxy_rotator():
    """Function that rotates proxies"""
    return storage.get('proxies')


@get_random
def useragent_rotator():
    """Function that rotates user agents"""
    return list(storage.get('user_agents'))


class Webscrapper:
    start_url = None
    initial_domain = None
    urls_to_visit = None
    visited_urls = set()

    def __init__(self, start_url):
        self.start_url = start_url
        self.initial_domain = urlparse(self.start_url)
        self.urls_to_visit = set([self.start_url])

        # address_visited.connect(None, sender=self)
        # post_init.connect(None, sender=self)

    @staticmethod
    def _get_url_object(url):
        return urlparse(url)

    def _get_page(self, url):
        self.visited_urls.add(url)

        proxy = {'http': proxy_rotator}
        user_agent = useragent_rotator

        try:
            response = requests.get(
                url,
                # proxies=proxy,
                headers={
                    'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'User-Agent': user_agent
                }
            )
        except Exception as e:
            print(e.args)
            return None
        else:
            if 400 <= response.status_code <= 500:
                logger.instance.info(f'Failed to visit: {url}')
            else:
                logger.instance.info(f'Visited url: {url}')
            address_visited.send(self, response=response, url=url)
            return response

    def _get_soup(self, response):
        """Returns the BeautifulSoup object
        of the current page"""
        return BeautifulSoup(response.content, 'html.parser')

    def _get_xml_page(rself, response):
        """Returns the XML object of the
        current page"""
        parser = etree.HTMLParser(encoding='utf-8', remove_comments=True)
        instance = etree.fromstring(response.content, parser)
        return instance

    def _get_page_urls(self, response):
        soup = self._get_soup(response)

        links_found = soup.find_all('a')
        for link in links_found:
            url = link.attrs.get('href', None)

            if url is None:
                continue

            # Sometimes we'll get paths (ex. /some-path),
            # so we need reconcile the domain and the latter
            if url.startswith('/'):
                url = urljoin(
                    f'{self.initial_domain.scheme}://{self.initial_domain.netloc}',
                    url
                )

            # Only visit urls from the same
            # domain to avoid exploring the
            # whole wide web
            incoming_url_domain = self._get_url_object(url)
            if incoming_url_domain.netloc != self.initial_domain.netloc:
                continue

            # By security, if the incoming url is the same as the
            # root url, makes no sense to add it in the pool
            if url == f'{self.initial_domain.scheme}://{self.initial_domain.netloc}{self.initial_domain.path}':
                continue

            # TODO: Put an option where we can skip
            # images from the urls to visit
            is_image = any([x in url for x in ['jpg', 'jpeg', 'png']])
            if is_image:
                continue

            # Additional security measure, if the url has already
            # been visited, do not add it to the current list. This
            # might seem redundant but it happens that when the scrapper
            # visit a new page and finds urls (including those that has
            # been visited), since they are no longer present in
            # URLS_TO_VISIT, they are added once again making a sort
            # of infinite loop where the URLS_TO_VISIT does not reach to 0
            if url in self.visited_urls:
                continue

            self.urls_to_visit.add(url)
        logger.instance.info(f'{len(links_found)} urls found')

    def start(self, response, xml=None):
        """A custom function where the user can
        define additional actions to run on the
        response"""
        pass

    def main(self):
        """Main entrypoint to the scrapper"""
        post_init.send(self)
        while self.urls_to_visit:
            url_to_visit = self.urls_to_visit.pop()

            # This is a security measure created in case
            # a page we have already visited escapes the
            # previous checks
            if url_to_visit in self.visited_urls:
                continue

            logger.instance.info(
                f'{len(self.urls_to_visit)} urls left to visit')
            response = self._get_page(url_to_visit)

            if response is None:
                continue

            self._get_page_urls(response)

            cache.set('urls_to_visit', list(self.urls_to_visit))
            cache.set('visited_urls', list(self.visited_urls))

            soup = self._get_soup(response)
            xml = self._get_xml_page(response)

            # TODO:Delegate both the response and the
            # soup to a user defined underlying function
            self.start(response, xml=xml)

            middlewares.run_middlewares(response, soup, xml)
            write_file('db.txt', middlewares.middleware_responses,
                       filetype='json')

            logger.instance.info(f'Waiting {WAIT_TIME} seconds')
            cache.persist('urls_to_visit')
            time.sleep(WAIT_TIME)


# scrapper = Webscrapper('http://gency313.fr')
# scrapper.main()
