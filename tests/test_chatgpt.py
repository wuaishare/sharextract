import unittest

from sharextract.extractors.chatgpt import ChatGPTShareExtractor
from sharextract.http import HttpResponse


class FakeClient:
    def get_json(self, url, headers=None):
        payload = {
            "title": "Shared test",
            "current_node": "b",
            "mapping": {
                "a": {
                    "id": "a",
                    "parent": None,
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Hello"]},
                        "create_time": 1,
                    },
                },
                "b": {
                    "id": "b",
                    "parent": "a",
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["World"]},
                        "create_time": 2,
                    },
                },
            },
        }
        return HttpResponse(url=url, content_type="application/json", body=b"{}"), payload


class ChatGPTExtractorTests(unittest.TestCase):
    def test_extracts_mapping_chain(self):
        extractor = ChatGPTShareExtractor(FakeClient())
        result = extractor.extract("https://chatgpt.com/share/abc")
        self.assertEqual(result.title, "Shared test")
        self.assertEqual([m.role for m in result.messages], ["user", "assistant"])
        self.assertIn("Hello", result.markdown)
        self.assertIn("World", result.markdown)


if __name__ == "__main__":
    unittest.main()
