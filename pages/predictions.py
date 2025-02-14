import streamlit as st
from datetime import datetime
from fetch_github_data import fetch_data_for_duration
from process_github_data import analyze_contributions
from util import predict_days_to_milestone, get_milestone_dates, format_date_ddmmyyyy

st.set_page_config(
    page_title = "GitHub Stat Checker",
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
# Title and input
st.title("GitHub Contribution Tracker")
with st.sidebar:
    form = st.container(border=True)
    username = form.text_input("Enter GitHub Username:")
    token = form.text_input("Enter GitHub Personal Access Token:", type="password", help="Help: [Create Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-personal-access-token-classic)")
    show_private = form.toggle("Show Private Contributions", value=True, help="Toggle to show/hide private contributions in stats. Requires a token with 'repo' scope.")
    
    # Add warning about token permissions if showing private contributions
    if show_private:
        form.info("To view private contributions, make sure your token has the 'repo' scope enabled.", icon="ℹ️")
    
    button_pressed = form.button("Track", type="primary")

    with st.container(border=True):
        st.page_link(
            "app.py", 
            label="Overview", 
            icon="✨",
            help="Check yout GitHub stats and contributions."
            )
        st.page_link(
            "./pages/predictions.py", 
            label="Predictions", 
            icon="⚡",
            help="Predict your GitHub contributions."
            )


if username and token and button_pressed:
    # Fetch data
    today = datetime.now().strftime("%Y-%m-%d")
    current_year = datetime.now().year
    current_jan1st = datetime(current_year, 1, 1).strftime("%Y-%m-%d")
    last_jan1st = datetime(current_year-1, 1, 1).strftime("%Y-%m-%d")
    last_dedc31st = datetime(current_year-1, 12, 31).strftime("%Y-%m-%d")

    year_data = fetch_data_for_duration(
        username, 
        token,
        from_date= last_jan1st,
        to_date= last_dedc31st
        )

    current_year_data = fetch_data_for_duration(
        username, 
        token,
        from_date= current_jan1st,
        to_date= today
        )
    
    # Process data
    whole_year_stats = analyze_contributions(year_data)
    current_year_stats = analyze_contributions(current_year_data)

    
    
    with st.container(border=True):
        # --- 365 days stats ---
        contribution_rate_ly = whole_year_stats.get('contribution_rate', 0)
        active_days_ly = whole_year_stats.get('active_days', 0)
        
        # --- Current year stats ---
        total_contributions = current_year_stats.get('total_contributions', 0)
        total_days = current_year_stats.get('total_days', 0)
        contribution_rate = current_year_stats.get('contribution_rate', 0)
        active_days = current_year_stats.get('active_days', 0)

    # --- Future Predictions ---
    if contribution_rate_ly == 0:
        growth_rate = 0
    else:
        growth_rate = ((contribution_rate - contribution_rate_ly) / contribution_rate_ly) * 100  # Growth in %

    # if active_days_ly == 0:
    #     active_days_growth = 0
    # else:
    #     active_days_growth = ((active_days - active_days_ly) / active_days_ly) * 100  # Growth in %

    remaining_days = 365 - total_days
    predicted_future_contributions = contribution_rate * remaining_days
    predicted_future_active_days = (active_days / total_days) * remaining_days


    with st.container():
        # --- Predictions & Trends ---
        st.markdown("#### :material/timeline: **Predictions & Trends**")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            label="Contribution Rate Growth",
            value=f"{growth_rate:.2f}%",
            delta="+Increasing" if growth_rate > 0 else "-Decreasing",
            help="Growth in contribution rate compared to last year",
            border=True
        )

        col2.metric(
            label="Predicted Contributions This Year",
            value=f"{predicted_future_contributions + total_contributions:.0f} commits",
            delta=f"{'-' if predicted_future_contributions<=0 else '+'}{predicted_future_contributions:.0f} commits",
            help="Total predicted commits this year, if user continues to contribute at the same rate",
            border=True
        )

        col3.metric(
            label="Predicted Active Days This Year",
            value=f"{predicted_future_active_days + active_days:.0f} days",
            delta=f"{'-' if predicted_future_active_days <= 0 else '+'} {predicted_future_active_days:.0f} days",
            delta_color="off" if predicted_future_active_days <= 0 else "normal",
            help="Total predicted active days this year, if user continues to contribute at the same rate",
            border=True
        )

    # Milestone goals
    milestones = [100, 500, 1000, 2000, 5000, 10000]
    with st.container():
        st.markdown("#### :material/done_all: Milestones Estimations")
        
        # User's current contributions
        current_contributions = current_year_stats.get("total_contributions", 0)
        if current_contributions == 0:
            st.error("No contributions found for the current year.")
            st.stop()
        # Calculate days required for each milestone
        milestone_predictions = {
            milestone: predict_days_to_milestone(current_contributions, milestone, contribution_rate)
            for milestone in milestones
        }

        contributions = current_year_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

        milestone_dates = get_milestone_dates(milestones, contributions, total_contributions, contribution_rate)


        # Display Milestones
    

        col1, col2 = st.columns(2, border=True)

        for i, (milestone, days) in enumerate(milestone_predictions.items()):
            col = col1 if i % 2 == 0 else col2  # Alternate between columns
            if total_contributions >= milestone:
                # Unlocked Milestone
                status = milestone_dates.get(milestone, 'Not Achieveable')
                date = ''
                if status != 'Not Achieveable':
                    date = format_date_ddmmyyyy(status)
                col.metric(
                    label=f"✅ Achieved Milestone: {milestone} commits",
                    value=f"{date}" if date else "Achieved",
                    delta="Achieved",
                )
                col.progress(100, text=f":blue[{total_contributions}/{milestone}]")
                col.divider()
                

            
            else:
                progress = min(100, (total_contributions / milestone) * 100)
                # Locked Milestone with Progress Bar
                status = milestone_dates.get(milestone, 'Not Achieveable')
                date = ''
                if status != 'Not Achieveable':
                    date = format_date_ddmmyyyy(status)
                col.metric(
                    label=f"Estimated days to {milestone} commits",
                    value=f"{date}" if date else "Not achievable",
                    delta=f"{days:.0f} days" if days != float('inf') else "Not achievable"
                )

                if progress > 0:
                    col.progress(progress / 100, text=f":blue[{total_contributions}/{milestone}]")
                    col.divider()



else:
    st.info("ℹ️ ***Enter your GitHub username and token in the sidebar to get started.***")