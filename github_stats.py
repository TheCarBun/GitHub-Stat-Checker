import requests

def fetch_contribution_data(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{
        user(login: "{username}") {{
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
