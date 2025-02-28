import streamlit as st
from streamlit import session_state as sst
import pandas as pd
from datetime import datetime
from process_github_data import *
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from util import load_css, format_date_ddmmyyyy
from fetch_github_data import *

color = "#26a641"
TOKEN = st.secrets["token"]

def main():
    st.set_page_config(
        page_title = "GitHub Stats",
        page_icon = "./static/icon.png",
        layout = "wide",
        menu_items={
            "About": """
            This is a Streamlit app that tracks your GitHub contributions and provides insights into your activity.  
            Built by [:red[TheCarBun]](https://github.com/TheCarBun/) & [:red[Pakagronglb]](https://github.com/pakagronglb)  
            GitHub: [:green[GitHub-Stats]](https://github.com/TheCarBun/GitHub-Stat-Checker)
            """,
            
            "Report a bug": "https://github.com/TheCarBun/GitHub-Stat-Checker/issues",
        }
    )

    # Initializing session state
    if 'username' not in sst:
        sst.username = ''
    if 'user_token' not in sst:
        sst.user_token = ''
    if 'token_present' not in sst:
        sst.token_present = False
    if 'button_pressed' not in sst:
        sst.button_pressed = False

    # Title and input
    title_col, star_col = st.columns([8.5,1.5], vertical_alignment="bottom")
    title_col.title("GitHub Stats")
    stars = fetch_star_count()
    star_col.link_button(f"⭐ Star :orange[(**{stars}**)]", 
                         "https://github.com/TheCarBun/GitHub-Stat-Checker", 
                         help=f"Give a star to this repository on GitHub. Current stars: {stars}",
                         use_container_width=True)
    with st.sidebar:
        # with st.expander("❓ How to Use This Tool"):
        #     st.write("""
        #     This tool analyzes your GitHub activity and predicts future contributions.
        #     - Enter your GitHub username.
        #     - View your stats and predictions.
        #     - Export the data for further analysis.
        #     """)
        form = st.container(border=True)
        sst.username = form.text_input("Enter GitHub Username:", value=sst.username)
        
        if form.toggle("I have a GitHub Access Token", value=sst.token_present, help="Toggle if you have a token. Create [Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)"):
            sst.token_present = True
        else:
            sst.token_present = False
        
        # Add warning about token permissions if showing private contributions
        if sst.token_present:
            sst.user_token = form.text_input("Enter GitHub Personal Access Token:", value=sst.user_token, type="password")
            sst.token = sst.user_token
        else:
            sst.token = TOKEN
        
        if form.button("Analyze", type="primary"):
            sst.button_pressed = True
      
    
    if sst.username and sst.token and sst.button_pressed:      
        with st.sidebar:
            with st.container(border=True):
                st.page_link(
                    "app.py", 
                    label="Overview", 
                    icon="✨",
                    help="ℹ️ Check your GitHub stats and contributions."
                    )
                st.page_link(
                    "./pages/predictions.py", 
                    label="Predictions", 
                    icon="⚡",
                    help="ℹ️ Predict your GitHub contributions."
                    )  
        # Fetch data
        cont_data = fetch_contribution_data(sst.username, sst.token)
        user_data = fetch_user_data(sst.username, sst.token)
        repo_data = fetch_repo_data(sst.username, sst.token)

        if "errors" in cont_data or "errors" in user_data or "errors" in repo_data:
            st.error("Error fetching data. Check your username/token.")
        else:
            # Process data
            cont_stats = process_contribution_data(cont_data)
            user_stats = process_user_data(user_data)

            # --- User Stats Summary ---
            st.markdown("### User Summary")
            with st.container():
                user_info, user_stats_info = st.columns([1,3], border=True, vertical_alignment="center")
                with user_info:
                    avatar_url = user_stats.get("avatar_url")
                    user_bio = user_stats.get("bio")
                    location = user_stats.get("location")
                    followers = user_stats.get("followers")
                    following = user_stats.get("following")
                    repositories = user_stats.get("repositories")
                    total_prs = user_stats.get("total_pullrequests")
                    total_issues = user_stats.get("total_issues")
                    created_at = datetime.strptime(user_stats.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
                    created_at = created_at.strftime("%Y-%m-%d")

                    custom_css = load_css()
                    st.markdown(f"""
                                <style>
                                {custom_css}
                                </style>
                                """, unsafe_allow_html=True)

                    st.markdown(f"""
                                <div class="user-container">
                                    <div class="user-card">
                                        <img src="{avatar_url}" alt="Avatar" class="avatar">
                                        <div class="username">{sst.username}</div>
                                        <div class="bio">{user_bio}</div>
                                        <div class="stats">
                                            <div class="stat">Location:<b> {location}</b></div>
                                            <div class="stat">Repos:<b> {repositories}</b></div>
                                            <div class="stat">Followers:<b> {followers}</b></div>
                                            <div class="stat">Following:<b> {following}</b></div>
                                            <div class="stat">PRs:<b> {total_prs}</b></div>
                                            <div class="stat">Issues:<b> {total_issues}</b></div>
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                with user_stats_info:
                    # --- Summary Stats ---
                    total_contributions = cont_stats.get("total_contributions", 0)
                    public_contributions = cont_stats.get("public_contributions", 0)
                    private_contributions = cont_stats.get("private_contributions", 0)
                    highest_contribution = cont_stats.get("highest_contribution", 0)
                    highest_contribution_date = cont_stats.get("highest_contribution_date", None)
                    today_commits = cont_stats.get("today_commits", 0)
                    current_streak = cont_stats.get("current_streak", 0)
                    longest_streak = cont_stats.get("longest_streak", 0)
                    days = cont_stats.get("days", [])

            
                    # Validate contribution data
                    if public_contributions == 0 and private_contributions == 0:
                        st.warning("No contributions found. If you have private repositories, make sure your token has the 'repo' scope.")
                
                    # Calculate contributions based on toggle
                    display_total = public_contributions + private_contributions
                    if private_contributions == 0:
                        st.info("No private contributions found. If you have private repositories, verify your token permissions.")

                    # Display summary metrics
                    if today_commits > 0:
                        st.markdown(f"#### 🔥 Today: {today_commits} commits")
                    col1, col2, col3 = st.columns(3, border=True)
                    col1.metric(
                        "Total Contributions", 
                        value= f"{display_total:,} commits",
                        delta=f"Public: {public_contributions:,} | Private: {private_contributions:,}",
                        delta_color= "off" if display_total == 0 else "normal"
                        )
                    col2.metric(
                        "Current Streak", 
                        value= f"{'☹️' if current_streak==0 else '🔥'} {current_streak} days",
                        delta=f"Longest: {longest_streak} days",
                        delta_color= "off" if current_streak == 0 else "normal"
                        )
                    col3.metric(
                        "Most Productive Day",
                        value= f"{highest_contribution} commits",
                        delta=f"{highest_contribution_date if highest_contribution>0 else 'No activity found'}",
                        delta_color="normal"
                        )
                    
                    # Days on GitHub & Active days
                    formatted_date = user_stats.get("formatted_date")
                    joined_since = user_stats.get("joined_since")
                    github_days = user_stats.get("github_days")
                    active_days = cont_stats.get("active_days")
                    less_than_2_months_old = user_stats.get("less_than_2_months_old")
            
            
                    col1, col2 = st.columns(2, border=True, vertical_alignment="center")
                    col1.metric(
                        label="Joined Github since",
                        value= formatted_date,
                        delta= joined_since,
                        delta_color= "inverse" if less_than_2_months_old else "normal"
                    )

                    col2.metric(
                        label="Total days on GitHub",
                        value= f"{github_days} days",
                        delta= f"Active for: {active_days} days",
                        delta_color= "off" if active_days < 7 else "normal"
                    )

                    

            # Prepare data for visualizations
            if not days:
                st.warning("No contribution data available for visualizations.")
            else:
                dates = [datetime.strptime(day["date"], "%Y-%m-%d") for day in days]
                # Add private contributions to daily counts if enabled
                contributions = [day.get("contributionCount", 0) for day in days]

                # --- Contributions Over Time ---
                st.markdown("### Contributions Over Time")
                with st.container(border=True):
                    chart_data = pd.DataFrame({"Date": dates, "Contributions": contributions})
                    st.line_chart(
                        chart_data.set_index("Date"), 
                        x_label="Date", 
                        y_label=f"Contributions", 
                        color=color
                    )

                # --- Growth and Statistics ---

                st.markdown("### Growth and Statistics")
                with st.container():
                    if sst.user_token:
                        # Fetch data
                        chart_data['Year'] = chart_data['Date'].dt.year
                        yearly_contributions = chart_data.groupby('Year')['Contributions'].sum().round(1)  # Round to 1 decimal
                    
                    # ------------- Last Year Contributions
                    with st.container(border=True):
                        st.markdown(f"#### :material/calendar_month: **Last year contributions({datetime.now().year-1}):**")
                        if sst.user_token:
                            # --- 365 days stats ---
                            last_jan1st = datetime(datetime.now().year-1, 1, 1).strftime("%Y-%m-%d")
                            last_dec31st = datetime(datetime.now().year-1, 12, 31).strftime("%Y-%m-%d")
                            from_date= last_jan1st
                            # Date comes between Jan 1st and Dec 31st. We use join date as start date
                            if last_jan1st < created_at < last_dec31st: 
                                year_data = fetch_data_for_duration(
                                    sst.username, 
                                    sst.token,
                                    from_date= created_at,
                                    to_date= last_dec31st
                                )
                                from_date = created_at
                            # Date comes after Dec 31st. Unable to calculate rate for last year
                            elif created_at >= last_dec31st:
                                year_data = None
                            # Date comes before Jan 1st. We use Jan 1st as starting date
                            else:
                                year_data = fetch_data_for_duration(
                                    sst.username, 
                                    sst.token,
                                    from_date= last_jan1st,
                                    to_date= last_dec31st
                                )
                            if year_data:
                                # Process data
                                whole_year_stats = analyze_contributions(year_data)

                                total_contributions_ly = whole_year_stats.get('total_contributions')
                                total_days_ly = whole_year_stats.get('total_days')
                                contribution_rate_ly = whole_year_stats.get('contribution_rate')
                                active_days_ly = whole_year_stats.get('active_days')
                                percent_active_days_ly = (whole_year_stats.get('active_days')/total_days_ly)*100

                                col1, col2 = st.columns(2)
                                col1.metric(
                                    label=f"Total Contributions {f'`(from:{format_date_ddmmyyyy(from_date)})`' if from_date != last_jan1st else ''}", 
                                    value=f"{total_contributions_ly} commits",
                                    delta=f"{contribution_rate_ly:.2f} contributions/day",
                                    delta_color="inverse" if contribution_rate_ly < 1 else "normal",
                                    border=True
                                    )
                                
                                col2.metric(
                                    label="Active Days", 
                                    value=f"{active_days_ly} days",
                                    delta=f"{percent_active_days_ly:.1f}% days active",
                                    delta_color="inverse" if percent_active_days_ly < 8 else "normal",
                                    border=True
                                    )
                            else:
                                st.info(f"No Data for year {datetime.now().year-1}")
                        else:
                            st.info("Create GitHub Access Token to view these stats")
                        
                        # --- Current year stats ---
                        st.markdown(f"#### :material/calendar_today: **Contributions in current year({datetime.now().year}):**")
                        if sst.user_token:
                            today = datetime.now().strftime("%Y-%m-%d")
                            current_jan1st = datetime(datetime.now().year, 1, 1).strftime("%Y-%m-%d")
                            
                            # Fetching current year data
                            current_year_data = fetch_data_for_duration(
                                sst.username, 
                                sst.token,
                                from_date= current_jan1st,
                                to_date= today
                                )
                            # Process data
                            current_year_stats = analyze_contributions(current_year_data)

                            total_contributions = current_year_stats.get('total_contributions')
                            total_days = current_year_stats.get('total_days')
                            contribution_rate = current_year_stats.get('contribution_rate')
                            active_days = current_year_stats.get('active_days')
                            percent_active_days = (current_year_stats.get('active_days')/total_days)*100

                            col1, col2 = st.columns(2)
                            col1.metric(
                                label="Total Contributions", 
                                value=f"{total_contributions} commits",
                                delta=f"{contribution_rate:.2f} contributions/day",
                                delta_color="inverse" if contribution_rate < 1 else "normal",
                                border=True
                                )
                            
                            col2.metric(
                                label="Active Days", 
                                value=f"{active_days}/{total_days} days",
                                delta=f"{percent_active_days:.1f}% days active",
                                delta_color="inverse" if percent_active_days < 8 else "normal",
                                border=True
                                )
                        else:
                            st.info("Create GitHub Access Token to view these stats")

                    st.markdown("### Visualizations:")
                    col1, col2 = st.columns(2, border=True, vertical_alignment="center")

                    col1.markdown("### Yearly Growth")
                    if sst.user_token:
                        col1.bar_chart(yearly_contributions, color=color)
                    else:
                        col1.info("Create GitHub Access Token to view these stats")

                    # Display monthly growth visualization in Jan-2023 format
                    with st.container(border=True):
                        st.markdown("### Monthly Growth")
                        if sst.user_token:
                            # Convert dates to datetime format
                            chart_data["Date"] = pd.to_datetime(chart_data["Date"])
                            
                            # Create year and month columns for grouping
                            chart_data["Sort_Key"] = chart_data["Date"].dt.strftime("%Y-%m")
                            
                            # Group and aggregate
                            monthly_data = chart_data.groupby("Sort_Key")["Contributions"].sum().reset_index()
                            monthly_data["Display_Date"] = pd.to_datetime(monthly_data["Sort_Key"] + "-01")
                            monthly_data = monthly_data.sort_values("Display_Date")
                            
                            # Create Plotly bar chart
                            fig = go.Figure(go.Bar(
                                x=monthly_data["Display_Date"].dt.strftime("%b %Y"),
                                y=monthly_data["Contributions"],
                                marker_color=color
                            ))
                            
                            # Update layout for dark theme compatibility
                            fig.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                margin=dict(l=20, r=20, t=20, b=20),
                                height=200,
                                xaxis=dict(
                                    showgrid=True,
                                    gridcolor='rgba(128,128,128,0.2)'
                                ),
                                yaxis=dict(
                                    showgrid=True,
                                    gridcolor='rgba(128,128,128,0.2)'
                                )
                            )
                            
                            # Display the Plotly chart
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        else:
                            st.info("Create GitHub Access Token to view these stats")

                    # --- Weekday vs. Weekend Contributions ---
                    col2.markdown("### Weekday vs. Weekend")
                    if sst.user_token:
                        with col2.container(border=True):
                            chart_data['IsWeekend'] = chart_data['Date'].dt.dayofweek >= 5
                            weekend_data = chart_data.groupby('IsWeekend')['Contributions'].sum().round(1)
                            weekend_data.index = ["Weekdays", "Weekends"]
                            st.bar_chart(weekend_data, color=color, horizontal=True)
                    else:
                        col2.info("Create GitHub Access Token to view these stats")

                    # --- Contributions by Day of Week ---
                    col2.markdown("### By Day of Week")
                    if sst.user_token:
                        with col2.container(border=True):
                            # Ensure the 'Date' column is properly converted to datetime
                            chart_data["Date"] = pd.to_datetime(chart_data["Date"])
                            chart_data["Day"] = chart_data["Date"].dt.day_name()

                            # Aggregate contributions by day of the week
                            day_totals = chart_data.groupby("Day")["Contributions"].sum()

                            # Create ordered lists for plotting (reversed order for top-to-bottom display)
                            correct_order = ["Sunday", "Saturday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday"]
                            values = [day_totals.get(day, 0) for day in correct_order]

                            # Create Plotly bar chart
                            fig = go.Figure(go.Bar(
                                x=values,
                                y=correct_order,
                                orientation='h',
                                marker_color=color
                            ))

                            # Update layout for dark theme compatibility
                            fig.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='white',
                                showlegend=False,
                                margin=dict(l=0, r=0, t=0, b=0),
                                height=150,  # Reduce the height of the chart
                                xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
                                yaxis=dict(showgrid=False)
                            )

                            # Display the Plotly chart
                            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    else:
                        col2.info("Create GitHub Access Token to view these stats")

            # Add Language Distribution
            st.markdown("### Programming Languages")
            if sst.user_token:

                # Fetch repository stats
                repo_stats = process_language_data(repo_data)
                
                if repo_stats:
                    with st.container(border=True):
                        col1, col2 = st.columns([3,1], vertical_alignment="center", gap="small")
                        # Sort languages by count and take top 6 languages
                        sorted_data = dict(sorted(repo_stats.items(), key=lambda x: x[1]['count'], reverse=True))
                        top_languages = dict(list(sorted_data.items())[:6])
                        
                        # Add "Others" category for remaining languages
                        remaining_languages = dict(list(sorted_data.items())[6:])
                        if remaining_languages:
                            others_count = sum(lang_data['count'] for lang_data in remaining_languages.values())
                            top_languages["Others"] = {"count": others_count, "color": "#808080"}  # Gray for "Others"
                        
                        # Create figure with fixed size
                        fig, ax = plt.subplots(figsize=(8, 8))
                        
                        # Calculate percentages
                        total = sum(lang_data["count"] for lang_data in sorted_data.values())
                        
                        # Extract colors from processed data
                        colors = [lang_data["color"] for lang_data in top_languages.values()]
                        
                        # Create pie chart
                        wedges, texts, autotexts = ax.pie(
                            [lang_data["count"] for lang_data in top_languages.values()],
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
                            "Repositories": [lang_data["count"] for lang_data in top_languages.values()],
                            "Percentage": [f"{lang_data['count'] / total:.1%}" for lang_data in top_languages.values()]
                        })
                        col1.dataframe(lang_df, hide_index=True)
                else:
                    st.warning("No language data available for the user's repositories.")
            else:
                st.info("Create GitHub Access Token to view these stats")

            # Custom Achievements (based on visible contributions)
            st.markdown("### Achievements")
            with st.container():
                if sst.user_token:
                    st.success("Keep growing your GitHub stats to unlock more achievements! 🚀", icon="💪")
                streak_cont, contr_cont = st.columns(2)
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
                with streak_cont.container(border=True):
                    st.subheader("🔥 Streak Achievements")
                    if sst.user_token:
                        com_cont = st.container(border=False)
                        inc_exp = st.expander(label="Locked Achievements", icon="🔒")
                        current_streak = current_streak
                        
                        for title, details in streak_achievements.items():
                            progress = min(100, (current_streak / details["required"]) * 100)
                            if current_streak >= details["required"]:
                                emoji = "✅"
                                com_cont.markdown(f"{emoji} **:green[{title}]** : *{details['criteria']}*")
                            else:
                                emoji = "🔒"
                                col1, col2 = inc_exp.columns([2, 1])
                                col1.markdown(f"{emoji} **:orange[{title}]**")
                                col1.markdown(f"*{details['criteria']}*")
                                col2.markdown(f"**Progress: :orange[:orange-background[{progress:.1f}%]]**")
                                if progress > 0:
                                    inc_exp.progress(progress / 100, text=f":blue[{current_streak}/{details['required']}]")
                                    inc_exp.divider()
                    else:
                        st.info("Create GitHub Access Token to view these stats")

                # Display Contribution Achievements
                total_contributions = cont_stats.get("total_contributions", 0)
                with contr_cont.container(border=True):
                    st.subheader("🏆 Contribution Achievements")
                    if sst.user_token:
                        com_cont = st.container(border=False)
                        inc_exp = st.expander(label="Locked Achievements", icon="🔒")
                        for title, details in contribution_achievements.items():
                            progress = min(100, (total_contributions / details["required"]) * 100)
                            if total_contributions >= details["required"]:
                                emoji = "✅"
                                com_cont.markdown(f"{emoji} **:green[{title}]** : *{details['criteria']}*")
                            else:
                                emoji = "🔒"
                                col1, col2 = inc_exp.columns([2, 1])
                                col1.markdown(f"{emoji} **:orange[{title}]**")
                                col1.markdown(f"*{details['criteria']}*")
                                col2.markdown(f"**Progress: :orange[:orange-background[{progress:.1f}%]]** ")
                                if progress > 0:
                                    inc_exp.progress(progress / 100, text=f":blue[{total_contributions}/{details['required']}]")
                                    inc_exp.divider()
                    else:
                        st.info("Create GitHub Access Token to view these stats")
    else:
        st.success("ℹ️ ***Enter your GitHub username in the sidebar to see your stats.***")


if __name__ == "__main__":
    main()