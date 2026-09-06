import unittest

from sharextract.http import SafeHttpClient
from sharextract.router import _extractors_for_strategy


class RouterTests(unittest.TestCase):
    def test_auto_orders_native_before_media_and_web(self):
        names = [x.name for x in _extractors_for_strategy("auto", SafeHttpClient())]
        self.assertEqual(names[:2], ["deepseek-share", "chatgpt-share"])
        self.assertEqual(names[-1], "generic-web")

    def test_web_strategy_is_generic_only(self):
        names = [x.name for x in _extractors_for_strategy("web", SafeHttpClient())]
        self.assertEqual(names, ["generic-web"])


if __name__ == "__main__":
    unittest.main()
