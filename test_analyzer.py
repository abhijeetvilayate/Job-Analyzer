import unittest
from analyzer import clean_json_response, validate_and_normalize

class TestAnalyzer(unittest.TestCase):
    def test_clean_json_direct(self):
        raw = '{"match_score": 85, "summary": "Great fit", "matched_keywords": ["python"], "missing_keywords": ["docker"]}'
        res = clean_json_response(raw)
        self.assertEqual(res["match_score"], 85)
        self.assertEqual(res["matched_keywords"], ["python"])
        self.assertEqual(res["missing_keywords"], ["docker"])

    def test_clean_json_markdown_wrapped(self):
        raw = '```json\n{"match_score": 70, "summary": "Good fit"}\n```'
        res = clean_json_response(raw)
        self.assertEqual(res["match_score"], 70)
        self.assertEqual(res["summary"], "Good fit")
        self.assertEqual(res["matched_keywords"], [])

    def test_clean_json_with_preamble(self):
        raw = 'Here is the analysis:\n{"match_score": 92, "summary": "Excellent"}\nHope this helps!'
        res = clean_json_response(raw)
        self.assertEqual(res["match_score"], 92)

    def test_validate_and_normalize_missing_keys(self):
        res = validate_and_normalize({})
        self.assertEqual(res["match_score"], 0)
        self.assertIn("summary", res)
        self.assertIsInstance(res["matched_keywords"], list)
        self.assertIsInstance(res["tailored_improvement_tips"], list)

if __name__ == "__main__":
    unittest.main()

