import unittest

from neptunia import middlewares
from bs4 import BeautifulSoup
from lxml import etree
from requests.models import Response


def load_test_page():
    with open('tests/html/test.html', mode='r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        parser = etree.HTMLParser(encoding='utf-8', remove_comments=True)
        xml = etree.fromstring(content, parser)
        response = Response()
        response.status_code = 200
        response._content = content
        return response, soup, xml


class TestMiddlewares(unittest.TestCase):
    def test_loading(self):
        self.assertTrue(len(middlewares.container) > 0)

    def _get_middleware(self, name):
        middleware = middlewares[name]
        return middleware

    def test_text_middleware(self):
        response, soup, xml = load_test_page()
        middleware = middlewares['TextMiddleware']
        middleware(response, soup, xml)
        # print(middleware.container)

    def test_seo_middleware(self):
        response, soup, xml = load_test_page()
        middleware = self._get_middleware('SEOMiddleware')
        middleware(response, soup, xml)
        self.assertTrue(len(middleware.audits) > 0)

    def test_email_middleware(self):
        response, soup, xml = load_test_page()
        middleware = self._get_middleware('EmailMiddleware')
        middleware(response, soup, xml)


if __name__ == '__main__':
    unittest.main()
