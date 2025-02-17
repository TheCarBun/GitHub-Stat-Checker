"""
Unit tests for GitHub activity prediction functions and visualizations.
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
import pandas as pd
from unittest.mock import patch, MagicMock
import requests
from fetch_repository_data import fetch_repository_details, get_user_repositories

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

class TestRepositoryData(unittest.TestCase):
    # ... existing code ...

class TestVisualizationData(unittest.TestCase):
    def setUp(self):
        # Sample contribution data
        self.sample_dates = [
            "2024-01-01", "2024-01-15", 
            "2024-02-01", "2024-02-15",
            "2024-03-01", "2024-03-15"
        ]
        self.sample_contributions = [5, 3, 4, 6, 2, 8]
        
        # Create test DataFrame
        self.test_data = pd.DataFrame({
            'date': [datetime.strptime(date, "%Y-%m-%d") for date in self.sample_dates],
            'contributions': self.sample_contributions
        })
    
    def test_monthly_contributions_aggregation(self):
        """Test that monthly contributions are correctly aggregated"""
        monthly_data = self.test_data.resample('M', on='date')['contributions'].sum()
        
        # Verify correct monthly totals
        self.assertEqual(monthly_data['2024-01-31'], 8)  # January total
        self.assertEqual(monthly_data['2024-02-29'], 10)  # February total
        self.assertEqual(monthly_data['2024-03-31'], 10)  # March total
        
        # Verify all months are present
        self.assertEqual(len(monthly_data), 3)
        
        # Verify chronological order
        self.assertTrue(all(monthly_data.index[i] <= monthly_data.index[i+1] 
                          for i in range(len(monthly_data)-1)))
    
    def test_monthly_contributions_empty_data(self):
        """Test handling of empty contribution data"""
        empty_data = pd.DataFrame(columns=['date', 'contributions'])
        monthly_data = empty_data.resample('M', on='date')['contributions'].sum()
        
        # Verify empty result
        self.assertEqual(len(monthly_data), 0)

if __name__ == '__main__':
    unittest.main() 