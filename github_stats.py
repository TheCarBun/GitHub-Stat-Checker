import requests

def fetch_contribution_data(username: str, token: str) -> dict:
    """Fetch GitHub contribution data for a user."""
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    {
        user(login: "%s") {
            name
            contributionsCollection {
                totalCommitContributions
                restrictedContributionsCount
                contributionCalendar {
                    totalContributions
                    weeks {
                        contributionDays {
                            contributionCount
                            date
                        }
                    }
                }
            }
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
                edges {
                    node {
                        name
                        primaryLanguage {
                            name
                            color
                        }
                    }
                }
            }
        }
    }
    """ % username
    try:
        response = requests.post(url, json={"query": query}, headers=headers)
        response.raise_for_status()  # Raises HTTPError if the response was unsuccessful
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"errors": str(e)}

def process_contribution_data(data):
    try:
        calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
        days = [day for week in calendar['weeks'] for day in week['contributionDays']]
        
        total_contributions = calendar['totalContributions']
        highest_contribution = max(day['contributionCount'] for day in days)
        
        current_streak = 0
        longest_streak = 0

        for day in days:
            if day['contributionCount'] > 0:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 0

        return {
            "total_contributions": total_contributions,
            "highest_contribution": highest_contribution,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "days": days
        }
    except KeyError:
        return {"errors": "Invalid data structure"}

def process_language_data(data: dict) -> dict:
    """Process GitHub data to get language statistics."""
    if not data or 'data' not in data or 'user' not in data['data']:
        return {}
    
    repositories = data['data']['user']['repositories']['edges']
    language_count = {}

    for repo in repositories:
        language = repo['node'].get('primaryLanguage')
        if language and language.get('name'):
            language_name = language['name']
            language_count[language_name] = language_count.get(language_name, 0) + 1

    return language_count
