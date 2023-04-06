from collections import deque
from typing import Any, List

from bs4 import BeautifulSoup
from requests.models import Response

class BaseMiddleware:
    def __call__(
        self,
        response: Response,
        soup: BeautifulSoup,
        xml: Any
    ) -> None: ...


class TextMixin:
    def get_text(self, soup: BeautifulSoup) -> list[str]: ...


class TextMiddleware(TextMixin, BaseMiddleware): ...


class EmailMiddleware(TextMixin, BaseMiddleware):
    container: set = ...


class ImageMiddleware(BaseMiddleware):
    container: deque = ...
    restricted_to: List = ...


class SEOMiddleware(BaseMiddleware):
    audits: deque = ...
    failed_urls: List = ...
    csv_file: List = ...
