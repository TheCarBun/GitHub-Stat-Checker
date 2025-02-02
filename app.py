import streamlit as st
import pandas as pd
from datetime import datetime
from github_stats import fetch_contribution_data, process_contribution_data, process_language_data, process_user_data
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="GitHub Stat Checker",
    page_icon="🟢"
)

# Title and input
st.title("GitHub Contribution Tracker")
with st.container(border=True):
    username = st.text_input("Enter GitHub Username:")
    token = st.text_input("Enter GitHub Personal Access Token:", type="password", help="Help: [Create Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)")
    show_private = st.toggle("Show Private Contributions", value=True, help="Toggle to show/hide private contributions in stats. Requires a token with 'repo' scope.")
    
    # Add warning about token permissions if showing private contributions
    if show_private:
        st.info("⚠️ To view private contributions, make sure your token has the 'repo' scope enabled.", icon="ℹ️")
    
    button_pressed = st.button("Track", type="primary")

color = "#26a641"

if username and token and button_pressed:
    # Fetch data
    raw_data = fetch_contribution_data(username, token)
    if "errors" in raw_data:
        st.error("Error fetching data. Check your username/token.")
    else:
        user_stats = process_user_data(raw_data)
        formatted_date = user_stats.get("formatted_date")

        joined_since = user_stats.get("joined_since")
        github_days = user_stats.get("github_days")
        active_days = user_stats.get("active_days")
        less_than_2_months_old = user_stats.get("less_than_2_months_old")
        
        st.header("User Stats")
        with st.container():
            col1, col2 = st.columns(2)
            col1.metric(
                label="Joined Github since",
                value= formatted_date,
                delta= joined_since,
                delta_color= "inverse" if less_than_2_months_old else "normal",
                border= True
            )

            col2.metric(
                label="Total days on GitHub",
                value= f"{github_days} days",
                delta= f"Active for: {active_days} days",
                delta_color= "off" if active_days < 7 else "normal",
                border= True
            )

        stats = process_contribution_data(raw_data)
        
        # Validate contribution data
        if stats.get('public_contributions', 0) == 0 and stats.get('private_contributions', 0) == 0:
            st.warning("No contributions found. If you have private repositories, make sure your token has the 'repo' scope.")
        
        # Calculate contributions based on toggle
        display_total = stats.get('public_contributions', 0)
        if show_private:
            display_total += stats.get('private_contributions', 0)
            if stats.get('private_contributions', 0) == 0:
                st.info("No private contributions found. If you have private repositories, verify your token permissions.")

        # Display summary metrics
        st.header("Summary Stats")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Total Contributions", 
                value= f"{display_total:,} commits",  # Add thousands separator
                delta=f"Public: {stats['public_contributions']:,}" + (f" | Private: {stats['private_contributions']:,}" if show_private else ""),
                delta_color= "off" if display_total == 0 else "normal"
                )
            col2.metric(
                "Longest Streak", 
                value= f"{stats['longest_streak']} days",
                delta=f"Current Streak: {stats['current_streak']} days",
                delta_color= "off" if stats['current_streak'] == 0 else "normal"
                )
            col3.metric(
                "Highest in a Day",
                value= f"{stats['highest_contribution']} commits",
                delta="Public" + (" + Private" if show_private else ""),
                delta_color="off"
                )

        # Prepare data for visualizations
        days = stats.get("days", [])
        if not days:
            st.warning("No contribution data available for visualizations.")
        else:
            dates = [datetime.strptime(day["date"], "%Y-%m-%d") for day in days]
            # Calculate the average daily private contributions to distribute them across days
            daily_private_ratio = (stats.get('private_contributions', 0) / len(days)) if len(days) > 0 and show_private else 0
            # Add private contributions to daily counts if enabled
            contributions = [day.get("contributionCount", 0) + daily_private_ratio for day in days]

            # Contributions Over Time
            st.header("Contributions Over Time")
            with st.container(border=True):
                chart_data = pd.DataFrame({"Date": dates, "Contributions": contributions})
                st.line_chart(
                    chart_data.set_index("Date"), 
                    x_label="Date", 
                    y_label=f"Contributions ({'Public + Private' if show_private else 'Public'})", 
                    color=color
                )

                # Add note about private contributions distribution
                if show_private and stats.get('private_contributions', 0) > 0:
                    st.caption("Note: Private contributions are distributed evenly across the time period as detailed daily data is not available.")

            # Yearly Growth
            chart_data['Year'] = chart_data['Date'].dt.year
            yearly_contributions = chart_data.groupby('Year')['Contributions'].sum().round(1)  # Round to 1 decimal

            st.header(f"Yearly Growth ({'Public + Private' if show_private else 'Public'})")
            with st.container(border=True):
                st.bar_chart(yearly_contributions, color=color)

            # Most Productive Days
            st.header("Most Productive Day")
            most_productive_day = chart_data.loc[chart_data['Contributions'].idxmax()]
            st.metric(
                "Date", 
                most_productive_day['Date'].strftime("%d-%m-%Y"), 
                delta=f"{most_productive_day['Contributions']:.1f} Contributions ({'Public + Private' if show_private else 'Public'})", 
                label_visibility="collapsed", 
                border=True
            )

            # Weekday vs. Weekend Contributions
            st.header(f"Weekday vs. Weekend Contributions ({'Public + Private' if show_private else 'Public'})")
            with st.container(border=True):
                chart_data['IsWeekend'] = chart_data['Date'].dt.dayofweek >= 5
                weekend_data = chart_data.groupby('IsWeekend')['Contributions'].sum().round(1)
                weekend_data.index = ["Weekdays", "Weekends"]
                st.bar_chart(weekend_data, color=color, horizontal=True)

            # Contributions by Day of Week
            st.header(f"Contributions by Day of Week ({'Public + Private' if show_private else 'Public'})")
            with st.container(border=True):
                # Add the Day column before grouping
                chart_data['Day'] = chart_data['Date'].dt.dayofweek
                day_of_week_data = chart_data.groupby("Day")['Contributions'].sum().round(1)
                day_of_week_data.index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                st.bar_chart(day_of_week_data, color=color, horizontal=True)

        # Custom Achievements (based on visible contributions)
        st.header("Achievements")
        with st.container(border=True):
            # Define achievements with their criteria and thresholds
            streak_achievements = {
                "Streak Beginner": {"required": 2, "criteria": "Made contributions for 2 consecutive days"},
                "Streak Novice": {"required": 7, "criteria": "Made contributions for 7 consecutive days"},
                "Streak Apprentice": {"required": 14, "criteria": "Made contributions for 14 consecutive days"},
                "Streak Journeyman": {"required": 30, "criteria": "Made contributions for 30 consecutive days"},
                "Streak Expert": {"required": 60, "criteria": "Made contributions for 60 consecutive days"},
                "Streak Master": {"required": 90, "criteria": "Made contributions for 90 consecutive days"},
                "Streak Legend": {"required": 120, "criteria": "Made contributions for 120+ consecutive days"}
            }

            contribution_achievements = {
                "Contributor": {"required": 50, "criteria": "Made your first 50 contributions"},
                "Regular Contributor": {"required": 100, "criteria": "Reached 100 total contributions"},
                "Active Contributor": {"required": 500, "criteria": "Reached 500 total contributions"},
                "Dedicated Contributor": {"required": 1000, "criteria": "Reached 1,000 total contributions"},
                "Seasoned Contributor": {"required": 5000, "criteria": "Reached 5,000 total contributions"},
                "GitHub Legend": {"required": 10000, "criteria": "Reached 10,000+ total contributions"}
            }

            # Display Streak Achievements
            st.subheader("🔥 Streak Achievements")
            current_streak = stats['current_streak']
            
            for title, details in streak_achievements.items():
                progress = min(100, (current_streak / details["required"]) * 100)
                if current_streak >= details["required"]:
                    emoji = "✅"
                    st.markdown(f"{emoji} **{title}** – {details['criteria']}")
                else:
                    emoji = "🔒"
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"{emoji} **{title}** – {details['criteria']}")
                    col2.markdown(f"Progress: {progress:.1f}%")
                    if progress > 0:
                        st.progress(progress / 100, text="")

            # Display Contribution Achievements
            st.subheader("🏆 Contribution Achievements")
            for title, details in contribution_achievements.items():
                progress = min(100, (display_total / details["required"]) * 100)
                if display_total >= details["required"]:
                    emoji = "✅"
                    st.markdown(f"{emoji} **{title}** – {details['criteria']}")
                else:
                    emoji = "🔒"
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"{emoji} **{title}** – {details['criteria']}")
                    col2.markdown(f"Progress: {progress:.1f}%")
                    if progress > 0:
                        st.progress(progress / 100, text="")

            st.info("Keep growing your GitHub stats to unlock more achievements! 🚀", icon="💪")

        # Add Language Distribution
        st.header("Programming Languages")
        language_data = process_language_data(raw_data)
        
        if language_data:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                # Sort languages by count and take top 6 languages
                sorted_data = dict(sorted(language_data.items(), key=lambda x: x[1], reverse=True))
                top_languages = dict(list(sorted_data.items())[:6])
                
                # Add "Others" category for remaining languages
                remaining_languages = dict(list(sorted_data.items())[6:])
                if remaining_languages:
                    others_count = sum(remaining_languages.values())
                    top_languages["Others"] = others_count
                
                # Create figure with fixed size
                fig, ax = plt.subplots(figsize=(8, 8))
                
                # Calculate percentages
                total = sum(sorted_data.values())
                
                # Get colors from the API response
                colors = []
                for lang in top_languages.keys():
                    if lang == "Others":
                        colors.append('#808080')  # Gray for Others
                    else:
                        # Find the color for this language in the raw data
                        for edge in raw_data['data']['user']['repositories']['edges']:
                            repo = edge['node']
                            if repo['primaryLanguage'] and repo['primaryLanguage']['name'] == lang:
                                colors.append(repo['primaryLanguage']['color'])
                                break
                        else:
                            colors.append('#808080')  # Fallback color if not found
                
                # Create pie chart
                wedges, texts, autotexts = ax.pie(
                    top_languages.values(),
                    labels=top_languages.keys(),
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=colors,
                    textprops={'color': 'white', 'fontsize': 12},
                    wedgeprops={'edgecolor': 'white', 'linewidth': 1}
                )
                
                ax.axis('equal')
                
                # Make the figure background transparent
                fig.patch.set_alpha(0.0)
                ax.patch.set_alpha(0.0)
                
                col2.pyplot(fig)
                
                # Display language breakdown in a table
                col1.markdown("#### Language Breakdown")
                lang_df = pd.DataFrame({
                    "Language": top_languages.keys(),
                    "Repositories": top_languages.values(),
                    "Percentage": [f"{count/total:.1%}" for count in top_languages.values()]
                })
                col1.dataframe(lang_df, hide_index=True)
        else:
            st.warning("No language data available for the user's repositories.")
