import unittest
from neptunia import config

class TestConfig(unittest.TestCase):
    def test_loading(self):
        self.assertEqual(
            config.settings.default_section,
            'DEFAULT'
        )
        self.assertEqual(
            config.settings.get('DEFAULT', 'user_agents_file'),
            'user_agents.csv'
        )


if __name__ == '__main__':
    unittest.main()
