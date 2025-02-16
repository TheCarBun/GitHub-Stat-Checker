"""
Functions for analyzing and predicting GitHub user activity based on historical data.
These functions use metrics such as total contributions, active days, and current year
activity to make predictions about user's future behavior and milestones.
"""

from datetime import datetime
from typing import Dict, List, Tuple, Union
import numpy as np
from dataclasses import dataclass

@dataclass
class LongTermActivity:
    lifetime_rate: float
    current_rate: float
    trend: str

def predict_long_term_activity(
    total_contributions: int,
    github_days: int,
    current_year_contributions: int,
    active_days: int
) -> LongTermActivity:
    """
    Predict long-term activity based on historical data.
    
    Args:
        total_contributions: Total number of contributions
        github_days: Total days since account creation
        current_year_contributions: Contributions in current year
        active_days: Total number of active days
    
    Returns:
        LongTermActivity object containing lifetime rate, current rate and trend
    """
    if github_days == 0 or active_days == 0:
        return LongTermActivity(0.0, 0.0, "insufficient data")
    
    lifetime_rate = total_contributions / github_days
    current_rate = current_year_contributions / active_days if active_days > 0 else 0
    
    trend = "increasing" if current_rate > lifetime_rate else \
            "stable" if current_rate == lifetime_rate else "decreasing"
    
    return LongTermActivity(
        round(lifetime_rate, 2),
        round(current_rate, 2),
        trend
    )

def predict_future_active_days(
    active_days: int,
    github_days: int,
    remaining_days: int
) -> float:
    """
    Predict number of active days for the remaining period.
    
    Args:
        active_days: Total number of active days
        github_days: Total days since account creation
        remaining_days: Number of days remaining in the period
    
    Returns:
        Predicted number of active days
    """
    if github_days == 0:
        return 0.0
    
    activity_rate = active_days / github_days
    return round(activity_rate * remaining_days, 1)

def predict_burnout(active_days_by_year: List[int]) -> str:
    """
    Analyze trend in yearly activity to predict potential burnout.
    
    Args:
        active_days_by_year: List of active days per year (most recent first)
    
    Returns:
        String describing the activity trend
    """
    if len(active_days_by_year) < 2:
        return "Insufficient data for burnout prediction"
    
    # Calculate year-over-year changes
    changes = [
        (curr - prev) / prev * 100 if prev > 0 else 0
        for curr, prev in zip(active_days_by_year[:-1], active_days_by_year[1:])
    ]
    
    avg_change = sum(changes) / len(changes)
    
    if avg_change < -20:
        return "Significant decrease in activity, potential burnout risk"
    elif avg_change < -5:
        return "Activity is gradually decreasing"
    elif avg_change > 20:
        return "Activity is significantly increasing"
    elif avg_change > 5:
        return "Activity is gradually increasing"
    else:
        return "Activity is stable"

def predict_consistency(active_days: int, github_days: int) -> Tuple[float, str]:
    """
    Calculate consistency score and classify user's contribution pattern.
    
    Args:
        active_days: Total number of active days
        github_days: Total days since account creation
    
    Returns:
        Tuple of (consistency score, classification)
    """
    if github_days == 0:
        return (0.0, "No activity")
    
    consistency_score = (active_days / github_days) * 100
    
    if consistency_score >= 80:
        classification = "Highly consistent contributor"
    elif consistency_score >= 50:
        classification = "Regular contributor"
    elif consistency_score >= 25:
        classification = "Occasional contributor"
    else:
        classification = "Sporadic contributor"
    
    return (round(consistency_score, 1), classification)

def predict_account_longevity(active_days_by_year: List[int]) -> str:
    """
    Estimate how long the account is likely to remain active.
    
    Args:
        active_days_by_year: List of active days per year (most recent first)
    
    Returns:
        String prediction of account longevity
    """
    if len(active_days_by_year) < 2:
        return "Insufficient data for longevity prediction"
    
    # Calculate rate of change in activity
    yearly_changes = [
        (curr - prev) / prev if prev > 0 else 0
        for curr, prev in zip(active_days_by_year[:-1], active_days_by_year[1:])
    ]
    
    avg_change = sum(yearly_changes) / len(yearly_changes)
    current_activity = active_days_by_year[0]
    
    if avg_change >= 0:
        return "Account shows sustained or increasing activity"
    
    # Estimate years until activity drops below threshold
    years_until_inactive = 0
    projected_activity = current_activity
    while projected_activity > 10 and years_until_inactive < 10:
        projected_activity *= (1 + avg_change)
        years_until_inactive += 1
    
    if years_until_inactive >= 10:
        return "Account likely to remain active for 10+ years"
    else:
        return f"Account activity may cease in ~{years_until_inactive:.1f} years"

def predict_effective_rate(
    total_contributions: int,
    active_days: int,
    github_days: int
) -> float:
    """
    Calculate effective contribution rate weighted by activity frequency.
    
    Args:
        total_contributions: Total number of contributions
        active_days: Total number of active days
        github_days: Total days since account creation
    
    Returns:
        Effective contribution rate
    """
    if active_days == 0 or github_days == 0:
        return 0.0
    
    activity_frequency = active_days / github_days
    raw_rate = total_contributions / github_days
    
    return round(raw_rate * activity_frequency, 2)

def predict_milestone(
    current_contributions: int,
    milestone: int,
    lifetime_rate: float
) -> float:
    """
    Predict days required to reach the next milestone.
    
    Args:
        current_contributions: Current total contributions
        milestone: Target milestone to reach
        lifetime_rate: Historical contribution rate
    
    Returns:
        Estimated days to reach milestone
    """
    if lifetime_rate <= 0:
        return float('inf')
    
    remaining_contributions = milestone - current_contributions
    if remaining_contributions <= 0:
        return 0.0
    
    return round(remaining_contributions / lifetime_rate, 1)

def run_all_predictions(user_data: Dict) -> Dict:
    """
    Run all prediction functions and return comprehensive analysis.
    
    Args:
        user_data: Dictionary containing all required user metrics
    
    Returns:
        Dictionary containing all predictions
    """
    try:
        # Calculate days since account creation
        created_date = datetime.strptime(user_data["created_at"], "%Y-%m-%d")
        github_days = (datetime.now() - created_date).days
        
        # Run all predictions
        long_term = predict_long_term_activity(
            user_data["total_contributions"],
            github_days,
            user_data["current_year_contributions"],
            user_data["active_days"]
        )
        
        remaining_days = 365 - datetime.now().timetuple().tm_yday
        future_active = predict_future_active_days(
            user_data["active_days"],
            github_days,
            remaining_days
        )
        
        burnout_prediction = predict_burnout(user_data["active_days_by_year"])
        
        consistency_score, consistency_class = predict_consistency(
            user_data["active_days"],
            github_days
        )
        
        longevity = predict_account_longevity(user_data["active_days_by_year"])
        
        effective_rate = predict_effective_rate(
            user_data["total_contributions"],
            user_data["active_days"],
            github_days
        )
        
        milestone_days = predict_milestone(
            user_data["total_contributions"],
            user_data.get("milestone", 10000),
            long_term.lifetime_rate
        )
        
        return {
            "long_term_activity": {
                "lifetime_rate": long_term.lifetime_rate,
                "current_rate": long_term.current_rate,
                "trend": long_term.trend
            },
            "future_active_days": future_active,
            "burnout": burnout_prediction,
            "consistency": {
                "score": consistency_score,
                "classification": consistency_class
            },
            "account_longevity": longevity,
            "effective_rate": effective_rate,
            "milestone": milestone_days
        }
        
    except KeyError as e:
        return {
            "error": f"Missing required field: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Error running predictions: {str(e)}"
        } 