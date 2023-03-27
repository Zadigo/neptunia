from functools import lru_cache
from pathlib import Path
from typing import Literal, Type
from urllib.parse import ParseResult

from bs4 import BeautifulSoup
from lxml import etree
from requests.models import Response

PROJECT_PATH: Path = ...


URL: Literal = ...


INITIAL_DOMAIN: ParseResult = ...


MIDDLEWARES: Literal['neptune.middlewares'] = ...


URLS_TO_VISIT: set[str] = ...


VISITED_URLS: set = ...


def get_url_object(url: str) -> ParseResult: ...


def read_file(filename: str) -> set[str]: ...


@lru_cache(maxsize=300)
def get_random(func) -> str: ...


@get_random
def proxy_rotator(filename='proxies') -> set[str]: ...


@get_random
def useragent_rotator(filename='user_agents') -> set[str]: ...


def get_page(url: str) -> Response: ...


def get_soup(response: Response) -> Type[BeautifulSoup]: ...


def get_xml_page(response: Response) -> etree.HTMLParser: ...


def get_page_urls(response: Response) -> None: ...


def main() -> None: ...
