import requests
from datetime import datetime
from util import format_duration, is_less_than_2_months_old, format_date


def fetch_contribution_data(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
            createdAt
            name
            contributionsCollection {{
                totalCommitContributions
                restrictedContributionsCount
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
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {{
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
        response = requests.post(url, json={"query": query}, headers=headers)
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
            highest_contribution = max(day['contributionCount'] for day in days)
        except (ValueError, KeyError):
            highest_contribution = 0
        
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

        return {
            "total_contributions": total_contributions,
            "public_contributions": public_contributions,
            "private_contributions": private_contributions,
            "highest_contribution": highest_contribution,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
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
    Returns a dictionary of languages and their usage counts.
    """
    try:
        # Get repositories from the user data
        repositories = data['data']['user']['repositories']['edges']
        
        # Process language data
        language_counts = {}
        
        for edge in repositories:
            repo = edge['node']
            if repo['primaryLanguage']:
                language = repo['primaryLanguage']['name']
                language_counts[language] = language_counts.get(language, 0) + 1
        
        return language_counts
    except Exception as e:
        print(f"Error processing language data: {str(e)}")
        return None

def process_user_data(data):
    user_data = data.get("data", {}).get("user", {})
    
    # Calculate total GitHub days
    created_at = user_data.get("createdAt")
    formatted_date = format_date(user_data.get("createdAt")) 

    less_than_2_months_old = is_less_than_2_months_old(created_at)
    github_days = (datetime.now() - datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")).days

    joined_since = format_duration(created_at)

    # Extract contribution days
    weeks = user_data.get("contributionsCollection", {}).get("contributionCalendar", {}).get("weeks", [])
    contribution_days = [day["date"] for week in weeks for day in week["contributionDays"] if day["contributionCount"] > 0]
    
    active_days = len(set(contribution_days))  # Unique active contribution days
    
    return {
        "created_at": created_at,
        "formatted_date": formatted_date,
        "joined_since": joined_since,
        "github_days": github_days,
        "active_days": active_days,
        "less_than_2_months_old": less_than_2_months_old
    }