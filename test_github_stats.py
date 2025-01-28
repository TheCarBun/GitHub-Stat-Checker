import unittest
from github_stats import process_language_data

class TestGitHubStats(unittest.TestCase):
    def setUp(self):
        # Mock data for testing
        self.mock_data = {
            "data": {
                "user": {
                    "repositories": {
                        "edges": [
                            {
                                "node": {
                                    "name": "repo1",
                                    "primaryLanguage": {
                                        "name": "Python",
                                        "color": "#3572A5"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo2",
                                    "primaryLanguage": {
                                        "name": "JavaScript",
                                        "color": "#f1e05a"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo3",
                                    "primaryLanguage": {
                                        "name": "Python",
                                        "color": "#3572A5"
                                    }
                                }
                            },
                            {
                                "node": {
                                    "name": "repo4",
                                    "primaryLanguage": None
                                }
                            }
                        ]
                    }
                }
            }
        }

    def test_process_language_data(self):
        # Test normal case
        result = process_language_data(self.mock_data)
        self.assertIsNotNone(result)
        self.assertEqual(result["Python"], 2)
        self.assertEqual(result["JavaScript"], 1)
        self.assertEqual(len(result), 2)  # Should not count None language

    def test_process_language_data_empty(self):
        # Test with empty data
        empty_data = {
            "data": {
                "user": {
                    "repositories": {
                        "edges": []
                    }
                }
            }
        }
        result = process_language_data(empty_data)
        self.assertEqual(result, {})

    def test_process_language_data_invalid(self):
        # Test with invalid data
        invalid_data = {"data": {"user": {}}}
        result = process_language_data(invalid_data)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main() 