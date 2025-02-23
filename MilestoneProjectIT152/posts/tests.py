from django.test import TestCase
from singletons.config_manager import ConfigManager

class ConfigManagerTestCase(TestCase):
    def test_singleton_behavior(self):
        config1 = ConfigManager()
        config2 = ConfigManager()

        self.assertIs(config1, config2)  # Both instances are the same
        config1.set_setting("DEFAULT_PAGE_SIZE", 50)
        self.assertEqual(config2.get_setting("DEFAULT_PAGE_SIZE"), 50)  # Both instances share the same settings