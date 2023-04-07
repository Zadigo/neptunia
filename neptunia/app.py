import csv
import itertools
import pathlib
import random
import threading
import time
from argparse import ArgumentParser
from functools import lru_cache
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from lxml import etree

from neptunia import cache, logger, middlewares

URL = 'http://gency313.fr'

INITIAL_DOMAIN = urlparse(URL)

MIDDLEWARES = 'neptune.middlewares'

URLS_TO_VISIT = set([URL])

VISITED_URLS = set()


def get_url_object(url):
    return urlparse(url)


def read_file(filename):
    project_path = cache.get('project_path')
    full_path = project_path[0] / f'neptunia/{filename}.csv'
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

    proxy_value = proxy_rotator
    proxy = {
        'http': proxy_value
    }
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

    links_found = soup.find_all('a')
    for link in links_found:
        url = link.attrs.get('href', None)

        if url is None:
            continue

        # Sometimes we'll get paths (ex. /some-path),
        # so we need reconcile the domain and the latter
        if url.startswith('/'):
            url = urljoin(
                f'{INITIAL_DOMAIN.scheme}://{INITIAL_DOMAIN.netloc}',
                url
            )

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

        # Additional security measure, if the url has already
        # been visited, do not add it to the current list. This
        # might seem redundant but it happens that when the scrapper
        # visit a new page and finds urls (including those that has
        # been visited), since they are no longer present in
        # URLS_TO_VISIT, they are added once again making a sort
        # of infinite loop where the URLS_TO_VISIT does not reach to 0
        if url in VISITED_URLS:
            continue

        URLS_TO_VISIT.add(url)
    logger.instance.info(f'{len(links_found)} urls found')


def main(url_filter_funcs=[]):
    """Main entry point for the webcrawler"""

    while URLS_TO_VISIT:
        url_to_visit = URLS_TO_VISIT.pop()

        # This is a security measure created in case
        # a page we have already visited escapes the
        # previous checks
        if url_to_visit in VISITED_URLS:
            continue

        logger.instance.info(f'{len(URLS_TO_VISIT)} urls left to visit')
        response = get_page(url_to_visit)

        if response is None:
            continue

        get_page_urls(response, url_filter_funcs=url_filter_funcs)

        cache.set('urls_to_visit', list(URLS_TO_VISIT))
        cache.set('visited_urls', list(VISITED_URLS))

        soup = get_soup(response)
        xml = get_xml_page(response)

        # TODO:Delegate both the response and the
        # soup to a user defined underlying function

        middlewares.run_middlewares(response, soup, xml)

        logger.instance.info('Waiting 10 seconds')
        # cache.persist('urls_to_visit')
        time.sleep(10)


if __name__ == '__main__':
    parser = ArgumentParser(description='Simple web crawler')
    parser.add_argument('-u', '--url', type=str)
    namespace = parser.parse_args()
    # main(debug=True)
