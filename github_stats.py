import requests
from datetime import datetime
from util import format_duration, is_less_than_2_months_old, format_iso_date, format_date_ddmmyyyy

BASE_URL = "https://api.github.com/graphql"

def fetch_user_data(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            name
            bio
            location
            createdAt
            avatarUrl
            followers {{
                totalCount
            }}
            following {{
                totalCount
            }}
            repositories(ownerAffiliations: OWNER, isFork: false){{
                totalCount
            }}
            contributionsCollection {{
                totalCommitContributions
                totalPullRequestContributions
                totalIssueContributions
                }}
        }}
    }}
    """
    try:
        response = requests.post(BASE_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"errors": str(e)}
    
def fetch_repo_data(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {{
                totalCount
                edges {{
                    node {{
                        name
                        primaryLanguage {{
                            name
                            color
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    try:
        response = requests.post(BASE_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"errors": str(e)}
    

def fetch_contribution_data(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            contributionsCollection {{
                restrictedContributionsCount
                totalPullRequestContributions
                totalIssueContributions
                contributionCalendar {{
                    totalContributions
                    weeks {{
                        contributionDays {{
                            contributionCount
                            date
                        }}
                    }}
                }}
            }}
        }}
    }}
    """
    try:
        response = requests.post(BASE_URL, json={"query": query}, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"errors": str(e)}

def process_contribution_data(data):
    try:
        contributions_collection = data['data']['user']['contributionsCollection']
        calendar = contributions_collection['contributionCalendar']
        days = [day for week in calendar['weeks'] for day in week['contributionDays']]
        
        # Safely get contribution counts with fallbacks to 0
        public_contributions = calendar.get('totalContributions', 0)
        private_contributions = contributions_collection.get('restrictedContributionsCount', 0)
        total_contributions = public_contributions + private_contributions
        
        # Ensure we have valid contribution counts
        if not isinstance(public_contributions, (int, float)):
            public_contributions = 0
        if not isinstance(private_contributions, (int, float)):
            private_contributions = 0
            
        # Calculate highest contribution
        try:
            highest_day = max(days, key=lambda day: day['contributionCount'])
            highest_contribution = highest_day['contributionCount']
            highest_contribution_date = format_date_ddmmyyyy(highest_day['date'])
        except (ValueError, KeyError):
            highest_contribution = 0
            highest_contribution_date = None
        
        current_streak = 0
        longest_streak = 0
        
        # Calculate streaks with validation
        try:
            for day in days:
                if day.get('contributionCount', 0) > 0:
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    current_streak = 0
        except (TypeError, KeyError):
            current_streak = 0
            longest_streak = 0

        # Extract contribution days
        weeks = calendar.get("weeks", [])
        contribution_days = [day["date"] for week in weeks for day in week["contributionDays"] if day["contributionCount"] > 0]
        active_days = len(set(contribution_days))  # Unique active contribution days

        return {
            "total_contributions": total_contributions,
            "public_contributions": public_contributions,
            "private_contributions": private_contributions,
            "highest_contribution": highest_contribution,
            "highest_contribution_date": highest_contribution_date,
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

def process_language_data(data):
    """
    Process the language data from GitHub API response.
    Returns a dictionary of languages with their usage counts and colors.
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


def process_user_data(data):
    """
    Process the user data from GitHub API response.
    Returns a dictionary of user info like username, bio, location, etc.
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