import requests
import streamlit as st
from datetime import datetime

BASE_URL = "https://api.github.com/graphql"

@st.cache_data(ttl=300)
def fetch_data_for_duration(username: str, token: str, from_date: str, to_date: str):
    """
    Fetch user data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing user data or error message.
    """
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
    {{ 
      user(login: "{username}") {{
        createdAt
        contributionsCollection(from: "{from_date}T00:00:00Z", to: "{to_date}T23:59:59Z") {{
          restrictedContributionsCount
          totalCommitContributions
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

@st.cache_data(ttl=300)    
def fetch_user_data(username: str, token: str):
    """
    Fetch user data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing user data or error message.
    """
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

@st.cache_data(ttl=300)
def fetch_repo_data(username: str, token: str):
    """
    Fetch repository data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing repository data or error message.
    """
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

@st.cache_data(ttl=300)
def fetch_contribution_data(username: str, token: str):
    """
    Fetch all-time contribution data from GitHub GraphQL API by iterating through years.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: Aggregated JSON-like response containing all-time contribution data.
    """
    # 1. Get user's creation date
    user_info = fetch_user_data(username, token)
    if "errors" in user_info:
        return user_info
    
    try:
        created_at_str = user_info['data']['user']['createdAt']
        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
        start_year = created_at.year
        end_year = datetime.now().year
        
        all_weeks = []
        total_contributions = 0
        restricted_contributions = 0
        total_commits = 0
        total_prs = 0
        total_issues = 0
        
        # 2. Fetch data year by year (GitHub GraphQL limit is 1 year per request)
        for year in range(start_year, end_year + 1):
            # First year starts from account creation date
            if year == start_year:
                from_date = created_at.strftime("%Y-%m-%d")
            else:
                from_date = f"{year}-01-01"

            # Last year ends at current date
            if year == end_year:
                to_date = datetime.now().strftime("%Y-%m-%d")
            else:
                to_date = f"{year}-12-31"
            
            year_data = fetch_data_for_duration(username, token, from_date, to_date)
            
            if "data" in year_data and year_data["data"]["user"]:
                collection = year_data["data"]["user"]["contributionsCollection"]
                calendar = collection["contributionCalendar"]
                
                all_weeks.extend(calendar.get("weeks", []))
                total_contributions += calendar.get("totalContributions", 0)
                restricted_contributions += collection.get("restrictedContributionsCount", 0)
                total_commits += collection.get("totalCommitContributions", 0)
                total_prs += collection.get("totalPullRequestContributions", 0)
                total_issues += collection.get("totalIssueContributions", 0)
            elif "errors" in year_data:
                return year_data
                
        # 3. Return aggregated structure compatible with process_contribution_data
        return {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "restrictedContributionsCount": restricted_contributions,
                        "totalCommitContributions": total_commits,
                        "totalPullRequestContributions": total_prs,
                        "totalIssueContributions": total_issues,
                        "contributionCalendar": {
                            "totalContributions": total_contributions,
                            "weeks": all_weeks
                        }
                    }
                }
            }
        }
    except Exception as e:
        return {"errors": str(e)}


@st.cache_data(ttl=300)
def fetch_star_count():
    """
    Returns the number of stars for the GitHub-Stat-Checker repository.
    """
    url = "https://api.github.com/repos/TheCarbun/GitHub-Stat-Checker"
    try:
        response = requests.get(url).json()
        return response.get('stargazers_count', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stars: {e}")
        return 0