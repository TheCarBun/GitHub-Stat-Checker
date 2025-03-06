from datetime import datetime
from utils.util import get_streaks, get_highest_contribution, get_active_days, get_todays_commits, format_duration, is_less_than_2_months_old, format_iso_date, format_date_ddmmyyyy

def process_contribution_data(data: dict):
    """
    Process the contribution data from GitHub API response.

    Args:
        data (dict): JSON response from GitHub API containing contribution data.

    Returns:
        dict: Processed contribution data including total contributions, highest contribution, streaks, and active days.
    """
    try:
        contributions_collection = data['data']['user']['contributionsCollection']
        calendar = contributions_collection['contributionCalendar']
        days = [day for week in calendar['weeks'] for day in week['contributionDays']]
        weeks = calendar.get("weeks", [])
        
        # Safely get contribution counts with fallbacks to 0
        public_contributions = calendar.get('totalContributions', 0)
        private_contributions = contributions_collection.get('restrictedContributionsCount', 0)
        total_contributions = public_contributions + private_contributions
            
        # Calculate highest contribution
        highest_contribution, highest_contribution_date = get_highest_contribution(days)
        
        # Calculate streaks with validation
        current_streak, longest_streak = get_streaks(days)

        # Calculate Active Days
        active_days = get_active_days(weeks)

        # Find today's commits
        today_commits = get_todays_commits(weeks)

        return {
            "total_contributions": total_contributions,
            "public_contributions": public_contributions,
            "private_contributions": private_contributions,
            "highest_contribution": highest_contribution,
            "highest_contribution_date": highest_contribution_date,
            "today_commits": today_commits,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "active_days": active_days,
            "days": days
        }
    except (KeyError, TypeError) as e:
        print(f"Error processing contribution data: {str(e)}")
        return {
            "total_contributions": 0,
            "public_contributions": 0,
            "private_contributions": 0,
            "highest_contribution": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "days": []
        }

def process_language_data(data: dict):
    """
    Process the language data from GitHub API response.

    Args:
        data (dict): JSON response from GitHub API containing repository data.

    Returns:
        dict: Dictionary of languages with their usage counts and colors.
    """
    try:
        # Get repositories from the user data
        repositories = data['data']['user']['repositories']['edges']
        
        # Process language data
        language_data = {}
        
        for edge in repositories:
            repo = edge['node']
            if repo['primaryLanguage']:
                language = repo['primaryLanguage']['name']
                color = repo['primaryLanguage'].get('color', '#808080')  # Default to grey if no color

                if language not in language_data:
                    language_data[language] = {'count': 0, 'color': color}

                language_data[language]['count'] += 1
        
        return language_data
    except Exception as e:
        print(f"Error processing language data: {str(e)}")
        return None

def process_user_data(data: dict):
    """
    Process the user data from GitHub API response.

    Args:
        data (dict): JSON response from GitHub API containing user data.

    Returns:
        dict: Processed user data including name, bio, location, followers, following, repositories, and contributions.
    """
    try:
        user_data = data['data']['user']
        
        # Calculate total GitHub days
        created_at = user_data.get("createdAt")
        formatted_date = format_iso_date(created_at) 

        less_than_2_months_old = is_less_than_2_months_old(created_at)
        github_days = (datetime.now() - datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")).days

        joined_since = format_duration(created_at)

        return {
            "name": user_data.get("name", ""),
            "bio": user_data.get("bio", ""),
            "location": user_data.get("location", ""),
            "created_at": created_at,
            "avatar_url": user_data.get("avatarUrl"),
            "followers": user_data.get("followers").get("totalCount", 0),
            "following": user_data.get("following").get("totalCount", 0),
            "repositories": user_data.get("repositories").get("totalCount", 0),
            "total_commits": user_data.get("contributionsCollection").get("totalCommitContributions", 0),
            "total_pullrequests": user_data.get("contributionsCollection").get("totalPullRequestContributions", 0),
            "total_issues": user_data.get("contributionsCollection").get("totalIssueContributions", 0),
            "formatted_date": formatted_date,
            "joined_since": joined_since,
            "github_days": github_days,
            "less_than_2_months_old": less_than_2_months_old
        }
    except (KeyError, TypeError) as e:
        print(f"Error processing contribution data: {str(e)}")
        return {
            "errors": str(e)
        }
    
   
def analyze_contributions(data):
    """Analyzes GitHub contribution data and provides key insights."""
    if not data:
        return None

    try:
        contributions = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        
        total_contributions = sum(
            day["contributionCount"] for week in contributions for day in week["contributionDays"]
        )
        total_days = sum(1 for week in contributions for day in week["contributionDays"])

        contribution_rate = total_contributions / total_days  # Contributions per day

        active_days = get_active_days(contributions)

        return {
            "total_contributions": total_contributions,
            "total_days": total_days,
            "active_days": active_days,
            "contribution_rate": round(contribution_rate, 2)
        }
    except Exception as e:
        print(f"Error processing contribution data: {str(e)}")
        return {"errors": str(e)}