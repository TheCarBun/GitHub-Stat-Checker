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

        # Display summary metrics
        st.header("Summary Stats")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            col1.metric(
                "Total Contributions", 
                value= f"{stats['total_contributions']} commits",
                delta=f"Highest in a day: {stats['highest_contribution']} commits",
                delta_color= "off" if stats['highest_contribution'] == 0 else "normal"
                )
            col2.metric(
                "Longest Streak", 
                value= f"{stats['longest_streak']} days",
                delta=f"Current Streak: {stats['current_streak']} days",
                delta_color= "off" if stats['current_streak'] == 0 else "normal"
                )

        # Prepare data for visualizations
        days = stats["days"]
        dates = [datetime.strptime(day["date"], "%Y-%m-%d") for day in days]
        contributions = [day["contributionCount"] for day in days]

        # Contributions Over Time
        st.header("Contributions Over Time")
        with st.container(border=True):
            chart_data = pd.DataFrame({"Date": dates, "Contributions": contributions})
            st.line_chart(chart_data.set_index("Date"), x_label="Date", y_label="Contributions", color=color)

        # Yearly Growth
        chart_data['Year'] = chart_data['Date'].dt.year
        yearly_contributions = chart_data.groupby('Year')['Contributions'].sum()

        st.header("Yearly Growth")
        with st.container(border=True):
            st.bar_chart(yearly_contributions, color=color)

        # Weekly Heatmap
        # st.header("Weekly Contribution Heatmap")
        chart_data["Week"] = chart_data['Date'].dt.isocalendar().week
        chart_data["Day"] = chart_data['Date'].dt.dayofweek

        # heatmap_data = chart_data.pivot_table(index="Day", columns="Week", values="Contributions", aggfunc="sum", fill_value=0)
        # st.write("**Heatmap (Day of Week vs. Week of Year)**")
        # st.dataframe(heatmap_data, use_container_width=True)

        # Most Productive Days
        st.header("Most Productive Day")
        most_productive_day = chart_data.loc[chart_data['Contributions'].idxmax()]
        st.metric(
            "Date", 
            most_productive_day['Date'].strftime("%d-%m-%Y"), 
            delta=f"{most_productive_day['Contributions']} Contributions", 
            label_visibility="collapsed", 
            border=True
            )

        # Weekday vs. Weekend Contributions
        st.header("Weekday vs. Weekend Contributions")
        with st.container(border=True):
            chart_data['IsWeekend'] = chart_data['Date'].dt.dayofweek >= 5
            weekend_data = chart_data.groupby('IsWeekend')['Contributions'].sum()
            weekend_data.index = ["Weekdays", "Weekends"]
            st.bar_chart(weekend_data, color=color, horizontal=True)

        # Contribution Times Analysis (if available)
        st.header("Contributions by Day of Week")
        with st.container(border=True):
            day_of_week_data = chart_data.groupby("Day")['Contributions'].sum()
            day_of_week_data.index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            st.bar_chart(day_of_week_data, color=color, horizontal=True)

        # Custom Achievements
        st.header("Achievements")
        with st.container(border=True):
            if stats['current_streak'] <= 2:
                st.markdown("🌱 **Streak Beginner**") 
            elif stats['current_streak'] > 2 and stats['current_streak'] <= 7:
                st.markdown("🌿 **Streak Novice**")
            elif stats['current_streak'] > 7 and stats['current_streak'] <= 14:
                st.markdown("🌳 **Streak Apprentice**") 
            elif stats['current_streak'] > 14 and stats['current_streak'] <= 30:
                st.markdown("⚔️ **Streak Journeyman**")
            elif stats['current_streak'] > 30 and stats['current_streak'] <= 60:
                st.markdown("🛡️ **Streak Expert**")
            elif stats['current_streak'] > 60 and stats['current_streak'] <= 90:
                st.markdown("🧙‍♂️ **Streak Master**")
            elif stats['current_streak'] > 90:
                st.markdown("🐉 **Streak Legend**") 

            
            if stats['total_contributions'] < 50:
                st.markdown("🌱 **Contributor**")
            elif stats['total_contributions'] >= 50 and stats['total_contributions'] < 100:
                st.markdown("🌿 **Regular Contributor**")
            elif stats['total_contributions'] >= 100 and stats['total_contributions'] < 500:
                st.markdown("🌳 **Active Contributor**")
            elif stats['total_contributions'] >= 500 and stats['total_contributions'] < 1000:
                st.markdown("⚔️ **Dedicated Contributor**")
            elif stats['total_contributions'] >= 1000 and stats['total_contributions'] < 5000:
                st.markdown("🛡️ **Seasoned Contributor**")
            elif stats['total_contributions'] >= 5000:
                st.markdown("🧙‍♂️ **GitHub Legend**")

            st.write("Keep growing your GitHub stats and unlock more achievements!")

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
