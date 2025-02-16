"""
Unit tests for GitHub activity prediction functions.
"""

import unittest
from datetime import datetime
from github_activity_predictions import (
    predict_long_term_activity,
    predict_future_active_days,
    predict_burnout,
    predict_consistency,
    predict_account_longevity,
    predict_effective_rate,
    predict_milestone,
    run_all_predictions
)

class TestGitHubPredictions(unittest.TestCase):
    def setUp(self):
        self.sample_user_data = {
            "created_at": "2020-01-01",
            "active_days": 200,
            "total_contributions": 5000,
            "current_year_contributions": 115,
            "current_year_active_days": 37,
            "active_days_by_year": [150, 100, 50],
            "milestone": 10000
        }
    
    def test_predict_long_term_activity(self):
        result = predict_long_term_activity(5000, 365, 115, 200)
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result, 'lifetime_rate'))
        self.assertTrue(hasattr(result, 'current_rate'))
        self.assertTrue(hasattr(result, 'trend'))
    
    def test_predict_future_active_days(self):
        result = predict_future_active_days(200, 365, 100)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
    
    def test_predict_burnout(self):
        result = predict_burnout([150, 100, 50])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_predict_consistency(self):
        score, classification = predict_consistency(200, 365)
        self.assertIsInstance(score, float)
        self.assertIsInstance(classification, str)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_predict_account_longevity(self):
        result = predict_account_longevity([150, 100, 50])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_predict_effective_rate(self):
        result = predict_effective_rate(5000, 200, 365)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
    
    def test_predict_milestone(self):
        result = predict_milestone(5000, 10000, 13.7)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
    
    def test_run_all_predictions(self):
        result = run_all_predictions(self.sample_user_data)
        self.assertIsInstance(result, dict)
        self.assertIn('long_term_activity', result)
        self.assertIn('future_active_days', result)
        self.assertIn('burnout', result)
        self.assertIn('consistency', result)
        self.assertIn('account_longevity', result)
        self.assertIn('effective_rate', result)
        self.assertIn('milestone', result)
    
    def test_edge_cases(self):
        # Test with zero values
        zero_result = predict_long_term_activity(0, 0, 0, 0)
        self.assertEqual(zero_result.trend, "insufficient data")
        
        # Test with negative values
        self.assertGreaterEqual(predict_effective_rate(-100, 200, 365), 0)
        
        # Test with missing data
        incomplete_data = {"created_at": "2020-01-01"}
        result = run_all_predictions(incomplete_data)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main() 