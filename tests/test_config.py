import unittest
from neptune import config, middlewares


class TestConfig(unittest.TestCase):
    def test_loading(self):
        self.assertEqual(config.settings.default_section, 'DEFAULT')


class TestMiddlewares(unittest.TestCase):
    def test_loading(self):
        self.assertTrue(len(middlewares.container) > 0)


if __name__ == '__main__':
    unittest.main()
