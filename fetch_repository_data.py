"""
Functions for fetching detailed repository information from GitHub's GraphQL API.
"""

import requests
from typing import Dict, Optional

def fetch_repository_details(username: str, repo_name: str, token: str) -> Dict:
    """
    Fetch detailed information about a specific repository using GitHub's GraphQL API.
    
    Args:
        username: GitHub username (repository owner)
        repo_name: Name of the repository
        token: GitHub personal access token
    
    Returns:
        Dictionary containing repository details
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    query = """
    query($owner: String!, $name: String!) {
        repository(owner: $owner, name: $name) {
            name
            description
            url
            createdAt
            updatedAt
            defaultBranchRef {
                name
            }
            refs(refPrefix: "refs/heads/", first: 100) {
                totalCount
                nodes {
                    name
                }
            }
            forks {
                totalCount
            }
            watchers {
                totalCount
            }
            stargazers {
                totalCount
            }
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                nodes {
                    name
                    color
                }
                edges {
                    size
                }
            }
            contributors: mentionableUsers(first: 10) {
                totalCount
                nodes {
                    login
                    avatarUrl
                    url
                }
            }
            commitComments {
                totalCount
            }
            pullRequests(states: [OPEN]) {
                totalCount
            }
            closedPRs: pullRequests(states: [CLOSED, MERGED]) {
                totalCount
            }
            openIssues: issues(states: [OPEN]) {
                totalCount
            }
            closedIssues: issues(states: [CLOSED]) {
                totalCount
            }
        }
    }
    """
    
    variables = {
        "owner": username,
        "name": repo_name
    }
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        if "errors" in result:
            return {"error": result["errors"][0]["message"]}
        
        return result["data"]["repository"]
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch repository data: {str(e)}"}
    except (KeyError, TypeError) as e:
        return {"error": f"Invalid response format: {str(e)}"}

def get_user_repositories(username: str, token: str) -> Dict:
    """
    Fetch list of repositories for a given user.
    
    Args:
        username: GitHub username
        token: GitHub personal access token
    
    Returns:
        Dictionary containing repository list
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    query = """
    query($username: String!) {
        user(login: $username) {
            repositories(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
                nodes {
                    name
                    description
                    updatedAt
                }
            }
        }
    }
    """
    
    variables = {
        "username": username
    }
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        if "errors" in result:
            return {"error": result["errors"][0]["message"]}
        
        return result["data"]["user"]["repositories"]["nodes"]
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch repositories list: {str(e)}"}
    except (KeyError, TypeError) as e:
        return {"error": f"Invalid response format: {str(e)}"} 