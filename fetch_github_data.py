import requests
import streamlit as st

BASE_URL = "https://api.github.com/graphql"

@st.cache_data(ttl=600)
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

@st.cache_data(ttl=600)    
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

@st.cache_data(ttl=600)
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

@st.cache_data(ttl=600)
def fetch_contribution_data(username: str, token: str):
    """
    Fetch contribution data from GitHub GraphQL API.

    Args:
        username (str): GitHub username.
        token (str): GitHub personal access token.

    Returns:
        dict: JSON response from GitHub API containing contribution data or error message.
    """
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
