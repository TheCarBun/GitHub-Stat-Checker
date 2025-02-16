"""
Unit tests for repository data fetching functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
from fetch_repository_data import fetch_repository_details, get_user_repositories

class TestRepositoryData(unittest.TestCase):
    def setUp(self):
        self.username = "test_user"
        self.repo_name = "test_repo"
        self.token = "test_token"
        
        # Sample repository details response
        self.sample_repo_details = {
            "data": {
                "repository": {
                    "name": "test_repo",
                    "description": "Test repository",
                    "url": "https://github.com/test_user/test_repo",
                    "defaultBranchRef": {
                        "name": "main"
                    },
                    "refs": {
                        "totalCount": 3,
                        "nodes": [{"name": "main"}, {"name": "dev"}]
                    },
                    "forks": {
                        "totalCount": 5
                    },
                    "watchers": {
                        "totalCount": 10
                    },
                    "stargazers": {
                        "totalCount": 15
                    },
                    "languages": {
                        "nodes": [
                            {"name": "Python", "color": "#3572A5"}
                        ],
                        "edges": [
                            {"size": 1000}
                        ]
                    },
                    "contributors": {
                        "totalCount": 3,
                        "nodes": [
                            {
                                "login": "test_user",
                                "avatarUrl": "https://github.com/test_user.png",
                                "url": "https://github.com/test_user"
                            }
                        ]
                    },
                    "commitComments": {
                        "totalCount": 20
                    },
                    "pullRequests": {
                        "totalCount": 5
                    },
                    "closedPRs": {
                        "totalCount": 15
                    },
                    "openIssues": {
                        "totalCount": 3
                    },
                    "closedIssues": {
                        "totalCount": 10
                    }
                }
            }
        }
        
        # Sample repositories list response
        self.sample_repos_list = {
            "data": {
                "user": {
                    "repositories": {
                        "nodes": [
                            {
                                "name": "repo1",
                                "description": "First repository",
                                "updatedAt": "2024-01-01T00:00:00Z"
                            },
                            {
                                "name": "repo2",
                                "description": "Second repository",
                                "updatedAt": "2024-01-02T00:00:00Z"
                            }
                        ]
                    }
                }
            }
        }
    
    @patch('requests.post')
    def test_fetch_repository_details_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_repo_details
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test function
        result = fetch_repository_details(self.username, self.repo_name, self.token)
        
        # Verify results
        self.assertEqual(result["name"], "test_repo")
        self.assertEqual(result["forks"]["totalCount"], 5)
        self.assertEqual(result["contributors"]["totalCount"], 3)
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertIn("Authorization", call_args["headers"])
        self.assertIn("query", call_args["json"])
    
    @patch('requests.post')
    def test_fetch_repository_details_error(self, mock_post):
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_post.return_value = mock_response
        
        # Test function
        result = fetch_repository_details(self.username, self.repo_name, self.token)
        
        # Verify error handling
        self.assertIn("error", result)
        self.assertIn("Failed to fetch repository data", result["error"])
    
    @patch('requests.post')
    def test_get_user_repositories_success(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_repos_list
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test function
        result = get_user_repositories(self.username, self.token)
        
        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "repo1")
        self.assertEqual(result[1]["name"], "repo2")
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        self.assertIn("Authorization", call_args["headers"])
        self.assertIn("query", call_args["json"])
    
    @patch('requests.post')
    def test_get_user_repositories_error(self, mock_post):
        # Setup mock error response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
        mock_post.return_value = mock_response
        
        # Test function
        result = get_user_repositories(self.username, self.token)
        
        # Verify error handling
        self.assertIn("error", result)
        self.assertIn("Failed to fetch repositories list", result["error"])

if __name__ == '__main__':
    unittest.main() 