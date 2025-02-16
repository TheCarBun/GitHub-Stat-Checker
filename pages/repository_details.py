"""
Streamlit page for displaying detailed repository information.
"""

import streamlit as st
from datetime import datetime
from fetch_repository_data import fetch_repository_details, get_user_repositories

st.set_page_config(
    page_title="GitHub Repository Details",
    page_icon="./static/icon.png",
    layout="wide",
    menu_items={
        "About": """
        This is a Streamlit app that tracks your GitHub contributions and provides insights into your activity.  
        Built by [:red[TheCarBun]](https://github.com/TheCarBun/) & [:red[Pakagronglb]](https://github.com/pakagronglb)  
        GitHub: [:green[GitHub-Stats]](https://github.com/TheCarBun/GitHub-Stat-Checker)
        """,
        "Report a bug": "https://github.com/TheCarBun/GitHub-Stat-Checker/issues",
    }
)

# Title and input
st.title("GitHub Repository Details")

with st.sidebar:
    form = st.container(border=True)
    username = form.text_input("Enter GitHub Username:")
    token = form.text_input(
        "Enter GitHub Personal Access Token:",
        type="password",
        help="Help: [Create Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)"
    )
    
    button_pressed = form.button("Fetch Repositories", type="primary")

    with st.container(border=True):
        st.page_link(
            "app.py",
            label="Overview",
            icon="✨",
            help="Check your GitHub stats and contributions."
        )
        st.page_link(
            "./pages/predictions.py",
            label="Predictions",
            icon="⚡",
            help="Predict your GitHub contributions."
        )
        st.page_link(
            "./pages/repository_details.py",
            label="Repository Details",
            icon="📊",
            help="View detailed repository statistics."
        )

if username and token and button_pressed:
    # Fetch user's repositories
    repositories = get_user_repositories(username, token)
    
    if isinstance(repositories, dict) and "error" in repositories:
        st.error(repositories["error"])
    else:
        # Create repository selector
        repo_options = [repo["name"] for repo in repositories]
        selected_repo = st.selectbox(
            "Select a repository:",
            repo_options,
            format_func=lambda x: f"{x} - {next((r['description'] for r in repositories if r['name'] == x), 'No description')}"
        )
        
        if selected_repo:
            # Fetch repository details
            repo_details = fetch_repository_details(username, selected_repo, token)
            
            if isinstance(repo_details, dict) and "error" in repo_details:
                st.error(repo_details["error"])
            else:
                # Display repository information
                st.markdown("### Repository Overview")
                
                # Basic Info
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Repository",
                        repo_details["name"],
                        help="Repository name",
                        border=True
                    )
                    
                with col2:
                    st.metric(
                        "Default Branch",
                        repo_details["defaultBranchRef"]["name"] if repo_details["defaultBranchRef"] else "N/A",
                        help="Default branch name",
                        border=True
                    )
                    
                with col3:
                    st.metric(
                        "Total Branches",
                        repo_details["refs"]["totalCount"],
                        help="Total number of branches",
                        border=True
                    )
                
                # Activity Metrics
                st.markdown("### Activity Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Stars",
                        repo_details["stargazers"]["totalCount"],
                        help="Number of stargazers",
                        border=True
                    )
                
                with col2:
                    st.metric(
                        "Forks",
                        repo_details["forks"]["totalCount"],
                        help="Number of forks",
                        border=True
                    )
                
                with col3:
                    st.metric(
                        "Watchers",
                        repo_details["watchers"]["totalCount"],
                        help="Number of watchers",
                        border=True
                    )
                
                with col4:
                    st.metric(
                        "Contributors",
                        repo_details["contributors"]["totalCount"],
                        help="Number of contributors",
                        border=True
                    )
                
                # Issues and PRs
                st.markdown("### Issues and Pull Requests")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Open Issues",
                        repo_details["openIssues"]["totalCount"],
                        help="Number of open issues",
                        border=True
                    )
                
                with col2:
                    st.metric(
                        "Closed Issues",
                        repo_details["closedIssues"]["totalCount"],
                        help="Number of closed issues",
                        border=True
                    )
                
                with col3:
                    st.metric(
                        "Open PRs",
                        repo_details["pullRequests"]["totalCount"],
                        help="Number of open pull requests",
                        border=True
                    )
                
                with col4:
                    st.metric(
                        "Closed PRs",
                        repo_details["closedPRs"]["totalCount"],
                        help="Number of closed/merged pull requests",
                        border=True
                    )
                
                # Languages
                if repo_details["languages"]["nodes"]:
                    st.markdown("### Programming Languages")
                    
                    total_size = sum(edge["size"] for edge in repo_details["languages"]["edges"])
                    
                    for node, edge in zip(repo_details["languages"]["nodes"], repo_details["languages"]["edges"]):
                        percentage = (edge["size"] / total_size) * 100
                        st.markdown(
                            f'<div style="display: flex; align-items: center; margin-bottom: 5px;">'
                            f'<div style="width: 12px; height: 12px; background-color: {node["color"]}; margin-right: 8px; border-radius: 50%;"></div>'
                            f'<div style="flex-grow: 1;">'
                            f'<div style="background-color: {node["color"]}30; border-radius: 4px; padding: 4px 8px;">'
                            f'{node["name"]}: {percentage:.1f}%'
                            f'</div>'
                            f'</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                
                # Contributors
                if repo_details["contributors"]["nodes"]:
                    st.markdown("### Top Contributors")
                    
                    cols = st.columns(5)
                    for i, contributor in enumerate(repo_details["contributors"]["nodes"]):
                        with cols[i % 5]:
                            st.markdown(
                                f'<div style="text-align: center;">'
                                f'<img src="{contributor["avatarUrl"]}" style="width: 64px; height: 64px; border-radius: 50%;">'
                                f'<p><a href="{contributor["url"]}" target="_blank">{contributor["login"]}</a></p>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

else:
    st.info("ℹ️ ***Enter your GitHub username and token in the sidebar to get started.***") 