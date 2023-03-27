import asyncio
import csv
import itertools
import logging
import pathlib
import random
from argparse import ArgumentParser
from functools import lru_cache
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree

PROJECT_PATH = pathlib.Path('.').absolute().joinpath('scrapper')

URL = 'http://example.com'

URLS_TO_VISIT = set([URL])

VISITED_URLS = set()

SKIP_URLS = []

LOGGER = {}


async def database():
    conection = None
    return conection


async def get_url_object(url):
    return urlparse(url)


def read_file(filename):
    full_path = PROJECT_PATH.joinpath(f'{filename}.csv')
    with open(full_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        data = itertools.chain(*list(reader))
        return set(data)


@lru_cache(maxsize=300)
async def get_random(func):
    values = await func()
    if not values:
        return None
    return random.choice(list(values))


@get_random
async def proxy_rotator(filename='proxies'):
    return read_file(filename)


@get_random
async def useragent_rotator(filename='user_agents'):
    return read_file(filename)


async def get_logger(name='main'):
    if name not in LOGGER:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        logger.addHandler(handler)

        log_format = logging.Formatter('%(asctime)s - [%(name)s] %(message)s')
        handler.setFormatter(log_format)

        LOGGER = logger
    else:
        return LOGGER[name]


async def log(name='main'):
    logger = await get_logger(name)
    return logger


async def retry_loop(url, max_retries=3):
    retry = 0
    response = None
    bad_proxies = set()
    for proxy in proxies:
        try:
            response = requests.get(
                url,
                proxies=proxy,
                headers={
                    'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'User-Agent': user_agent
                }
            )
        except requests.exceptions.ConnectTimeout:
            bad_proxies.add(proxy)
        else:
            response = response
            retry = retry + 1
            if retry > max_retries:
                break

    return response


async def get_page(url):
    VISITED_URLS.add(url)

    proxy = {'http': await proxy_rotator}
    user_agent = await useragent_rotator

    response = requests.get(
        url,
        proxies=proxy,
        headers={
            'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': user_agent
        }
    )
    print('Visited url:', url, '-> proxy:', proxy)
    # logger = await log()
    # logger.info(f'Sent request for {url}')
    return response


async def get_soup(response):
    return BeautifulSoup(response.content, 'html.parser')


async def get_xml_page(response):
    parser = etree.HTMLParser(encoding='utf-8', remove_comments=True)
    instance = etree.fromstring(response.content, parser)
    return instance


async def get_page_urls(response):
    soup = await get_soup(response)

    # Only visit urls from the same
    # domain to avoid exploring the
    # whole wide web
    initial_domain = await get_url_object(URL)

    for link in soup.find_all('a'):
        url = link.attrs.get('href', None)
        if url is None or not url.startswith('http'):
            continue

        incoming_url_domain = await get_url_object(url)
        if initial_domain.netloc not in incoming_url_domain.netloc:
            continue

        # TODO: Also, check that the url is not a file or
        # other types of known extensions if this
        # was specified

        URLS_TO_VISIT.add(url)

    print(len(URLS_TO_VISIT), 'to visit')


async def main(analyzer=None):
    if analyzer is not None:
        if not callable(analyzer):
            raise ValueError('Analyzer should be a function')

    while URLS_TO_VISIT:
        url_to_visit = URLS_TO_VISIT.pop()
        response = await get_page(url_to_visit)
        await get_page_urls(response)

        # Delegate both the response and the
        # soup to a user defined underlying function
        if analyzer is not None:
            soup = await get_soup(response)
            xml = await get_xml_page(response)
            await analyzer(response, soup=soup, xml=xml)
        asyncio.sleep(10)


async def test_analyzer(response, **kwargs):
    pass


if __name__ == '__main__':
    asyncio.run(main(analyzer=test_analyzer))
