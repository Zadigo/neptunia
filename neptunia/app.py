import csv
import itertools
import pathlib
import random
import threading
import time
from functools import lru_cache
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree

from neptunia import cache, logger, middlewares

PROJECT_PATH = pathlib.Path('.').absolute()

# URL = 'https://www.hotelgeorgette.com/'
# URL = 'http://example.com'
URL = 'http://johnpm.fr'

INITIAL_DOMAIN = urlparse(URL)

MIDDLEWARES = 'neptune.middlewares'

URLS_TO_VISIT = set([URL])

VISITED_URLS = set()


def database():
    conection = None
    return conection


def get_url_object(url):
    return urlparse(url)


def read_file(filename):
    # full_path = PROJECT_PATH.joinpath(f'{filename}.csv')
    full_path = f'D:/personnal/neptune/neptune/{filename}.csv'
    with open(full_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        data = itertools.chain(*list(reader))
        return set(data)


@lru_cache(maxsize=300)
def get_random(func):
    values = func()
    if not values:
        return None
    return random.choice(list(values))


@get_random
def proxy_rotator(filename='proxies'):
    return read_file(filename)


@get_random
def useragent_rotator(filename='user_agents'):
    return read_file(filename)


def get_page(url):
    VISITED_URLS.add(url)

    proxy = {'http': proxy_rotator}
    user_agent = useragent_rotator

    response = requests.get(
        url,
        # proxies=proxy,
        headers={
            'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': user_agent
        }
    )
    logger.instance.info(f'Visited url: {url}')
    return response


def get_soup(response):
    return BeautifulSoup(response.content, 'html.parser')


def get_xml_page(response):
    parser = etree.HTMLParser(encoding='utf-8', remove_comments=True)
    instance = etree.fromstring(response.content, parser)
    return instance


def get_page_urls(response, url_filter_funcs=[]):
    """Return all the urls of the
    currently visited page"""
    soup = get_soup(response)

    for link in soup.find_all('a'):
        url = link.attrs.get('href', None)

        if url is None:
            continue

        # Sometimes we'll get paths so we need
        # reconcile the domain and the latter
        if url.startswith('/'):
            url = urljoin(f'https://{INITIAL_DOMAIN.netloc}', url)

        # Only visit urls from the same
        # domain to avoid exploring the
        # whole wide web
        incoming_url_domain = get_url_object(url)
        if incoming_url_domain.netloc != INITIAL_DOMAIN.netloc:
            continue

        # By security, if the incoming url is the same as the
        # root url, makes no sense to add it in the pool
        if url == f'{INITIAL_DOMAIN.scheme}://{INITIAL_DOMAIN.netloc}{INITIAL_DOMAIN.path}':
            continue

        # TODO: Put an option where we can skip
        # images from the urls to visit
        is_image = any([x in url for x in ['jpg', 'jpeg', 'png']])
        if is_image:
            continue

        URLS_TO_VISIT.add(url)
    logger.instance.info(f'{len(URLS_TO_VISIT)} urls to visit')


# class Main:
#     _urls_to_visit = []

#     def run(self, url):
#         self._urls_to_visit = [url]

#         while URLS_TO_VISIT:
#             url_to_visit = self._urls_to_visit.pop()
#             response = get_page(url_to_visit)
#             get_page_urls(response)

#             cache.set('urls_to_visit', list(self._urls_to_visit))

#             # Delegate both the response and the
#             # soup to a user defined underlying function
#             soup = get_soup(response)
#             xml = get_xml_page(response)

#             middlewares.run_middlewares(response, soup, xml)

#             logger.instance.info('Waiting 10 seconds')
#             # cache.persist('urls_to_visit')
#             time.sleep(10)


def test_server():
    while True:
        print('Running test server')
        time.sleep(10)


def main(url_filter_funcs=[]):
    """Main entry point for the
    webcrawler"""

    while URLS_TO_VISIT:
        url_to_visit = URLS_TO_VISIT.pop()
        response = get_page(url_to_visit)
        get_page_urls(response, url_filter_funcs=url_filter_funcs)

        cache.set('urls_to_visit', list(URLS_TO_VISIT))

        # Delegate both the response and the
        # soup to a user defined underlying function
        soup = get_soup(response)
        xml = get_xml_page(response)

        middlewares.run_middlewares(response, soup, xml)

        logger.instance.info('Waiting 10 seconds')
        # cache.persist('urls_to_visit')
        print(URLS_TO_VISIT)
        time.sleep(10)


if __name__ == '__main__':
    # thread = threading.Thread(target=main)
    # thread.name = 'crawler'
    # thread.start()
    # main()
    test_server()
