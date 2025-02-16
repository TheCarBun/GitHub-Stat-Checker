import streamlit as st
from datetime import datetime
import pandas as pd
from fetch_github_data import fetch_data_for_duration
from process_github_data import analyze_contributions
from util import predict_days_to_milestone, get_milestone_dates, format_date_ddmmyyyy
from github_activity_predictions import (
    predict_long_term_activity,
    predict_burnout,
    predict_consistency,
    predict_account_longevity,
    predict_effective_rate
)

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
        st.page_link(
            "./pages/repository_details.py",
            label="Repository Details",
            icon="📊",
            help="View detailed repository statistics."
        )


if username and token and button_pressed:
    try:
        # Fetch data with proper date ranges
        today = datetime.now()
        current_year = today.year
        
        # Calculate date ranges
        current_jan1st = datetime(current_year, 1, 1)
        last_jan1st = datetime(current_year - 1, 1, 1)
        last_dec31st = datetime(current_year - 1, 12, 31)
        
        # Format dates for API
        today_str = today.strftime("%Y-%m-%d")
        current_jan1st_str = current_jan1st.strftime("%Y-%m-%d")
        last_jan1st_str = last_jan1st.strftime("%Y-%m-%d")
        last_dec31st_str = last_dec31st.strftime("%Y-%m-%d")

        # Fetch data for both periods
        year_data = fetch_data_for_duration(
            username,
            token,
            from_date=last_jan1st_str,
            to_date=last_dec31st_str
        )

        current_year_data = fetch_data_for_duration(
            username,
            token,
            from_date=current_jan1st_str,
            to_date=today_str
        )
        
        if not year_data or not current_year_data:
            st.error("Failed to fetch GitHub data. Please check your username and token.")
            st.stop()
        
        # Process data
        whole_year_stats = analyze_contributions(year_data)
        current_year_stats = analyze_contributions(current_year_data)
        
        # Calculate basic metrics
        total_days = (today - current_jan1st).days + 1
        remaining_days = max(0, 365 - total_days)
        
        contribution_rate_ly = whole_year_stats.get('contribution_rate', 0)
        active_days_ly = whole_year_stats.get('active_days', 0)
        total_contributions = current_year_stats.get('total_contributions', 0)
        contribution_rate = current_year_stats.get('contribution_rate', 0)
        active_days = current_year_stats.get('active_days', 0)
        
        # Calculate growth rates safely
        if contribution_rate_ly > 0:
            growth_rate = ((contribution_rate - contribution_rate_ly) / contribution_rate_ly) * 100
        else:
            growth_rate = 0 if contribution_rate == 0 else 100
        
        # Calculate predictions safely
        if total_days > 0:
            daily_rate = total_contributions / total_days
            active_rate = active_days / total_days
        else:
            daily_rate = 0
            active_rate = 0
        
        predicted_future_contributions = daily_rate * remaining_days
        predicted_future_active_days = active_rate * remaining_days
        
        # Display predictions
        with st.container():
            st.markdown("### 📊 Predictions & Trends")
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                label="Contribution Rate Growth",
                value=f"{growth_rate:.1f}%",
                delta="+Increasing" if growth_rate > 0 else "-Decreasing" if growth_rate < 0 else "Stable",
                help="Growth in contribution rate compared to last year",
                border=True
            )
            
            col2.metric(
                label="Predicted Year-End Contributions",
                value=f"{int(total_contributions + predicted_future_contributions)} commits",
                delta=f"+{int(predicted_future_contributions)} commits",
                help="Estimated total commits by year end at current rate",
                border=True
            )
            
            col3.metric(
                label="Predicted Active Days",
                value=f"{int(active_days + predicted_future_active_days)} days",
                delta=f"+{int(predicted_future_active_days)} days",
                help="Estimated total active days by year end at current rate",
                border=True
            )

        # Visualizations
        st.markdown("### 📈 Activity Visualizations")
        col1, col2 = st.columns(2, gap="medium")

        # Prepare data for visualizations
        contributions_data = []
        for week in current_year_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                contributions_data.append({
                    "date": datetime.strptime(day["date"], "%Y-%m-%d"),
                    "contributions": day["contributionCount"]
                })
        
        chart_data = pd.DataFrame(contributions_data)
        
        # Yearly Growth
        with col1:
            st.markdown("#### Yearly Growth")
            yearly_contributions = chart_data.groupby(chart_data['date'].dt.year)['contributions'].sum()
            st.bar_chart(yearly_contributions, use_container_width=True)
            
            # Monthly Contributions
            st.markdown("#### Monthly Contributions")
            monthly_contributions = chart_data.groupby(chart_data['date'].dt.strftime('%B'))['contributions'].sum()
            # Reorder months chronologically
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            monthly_contributions = monthly_contributions.reindex(month_order)
            st.bar_chart(monthly_contributions, use_container_width=True)

        # Activity Patterns
        with col2:
            st.markdown("#### Weekday vs. Weekend")
            weekend_data = chart_data.assign(
                is_weekend=chart_data['date'].dt.dayofweek.isin([5, 6])
            ).groupby('is_weekend')['contributions'].sum()
            weekend_data.index = ['Weekdays', 'Weekends']
            st.bar_chart(weekend_data, use_container_width=True)
            
            st.markdown("#### Daily Activity Pattern")
            daily_data = chart_data.groupby(chart_data['date'].dt.day_name())['contributions'].sum()
            # Reorder days of week
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_data = daily_data.reindex(day_order)
            st.bar_chart(daily_data, use_container_width=True)

        # Advanced Predictions
        with st.container():
            st.markdown("### 🔮 Advanced Activity Analysis")
            
            # Calculate advanced metrics
            long_term = predict_long_term_activity(
                total_contributions,
                total_days,
                current_year_stats.get("total_contributions", 0),
                active_days
            )
            
            consistency_score, consistency_class = predict_consistency(active_days, total_days)
            
            effective_rate = predict_effective_rate(
                total_contributions,
                active_days,
                total_days
            )
            
            # Historical data for burnout prediction
            active_days_by_year = [
                current_year_stats.get("active_days", 0),
                whole_year_stats.get("active_days", 0)
            ]
            
            burnout_prediction = predict_burnout(active_days_by_year)
            longevity_prediction = predict_account_longevity(active_days_by_year)
            
            # Display advanced metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Lifetime Contribution Rate",
                    value=f"{long_term.lifetime_rate:.2f} commits/day",
                    delta=long_term.trend.title(),
                    help="Average contributions per day over account lifetime",
                    border=True
                )
                
                st.metric(
                    label="Contribution Consistency",
                    value=f"{consistency_score:.1f}%",
                    delta=consistency_class,
                    help="How consistently you contribute (higher is better)",
                    border=True
                )
                
                st.metric(
                    label="Effective Contribution Rate",
                    value=f"{effective_rate:.2f} commits/active day",
                    help="Average contributions per active day, weighted by activity",
                    border=True
                )
            
            with col2:
                st.info(
                    f"**Activity Trend Analysis**\n{burnout_prediction}",
                    icon="📈"
                )
                
                st.info(
                    f"**Account Longevity Prediction**\n{longevity_prediction}",
                    icon="⏳"
                )
        
        # Milestones
        with st.container():
            st.markdown("### 🎯 Milestone Predictions")
            
            if total_contributions > 0:
                milestones = [100, 500, 1000, 2000, 5000, 10000]
                
                # Calculate milestone predictions
                milestone_predictions = {
                    milestone: predict_days_to_milestone(
                        total_contributions,
                        milestone,
                        max(0.1, contribution_rate)  # Ensure non-zero rate
                    ) for milestone in milestones
                }
                
                # Get milestone dates
                contributions = current_year_data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
                milestone_dates = get_milestone_dates(
                    milestones,
                    contributions,
                    total_contributions,
                    max(0.1, contribution_rate)  # Ensure non-zero rate
                )
                
                # Display milestones
                col1, col2 = st.columns(2)
                
                for i, (milestone, days) in enumerate(milestone_predictions.items()):
                    col = col1 if i % 2 == 0 else col2
                    
                    if total_contributions >= milestone:
                        # Achieved milestone
                        col.metric(
                            label=f"✅ {milestone:,} Commits",
                            value="Achieved!",
                            delta="Complete",
                            help=f"You've reached the {milestone:,} commits milestone",
                            border=True
                        )
                    else:
                        # Future milestone
                        progress = (total_contributions / milestone) * 100
                        eta_date = milestone_dates.get(milestone)
                        
                        col.metric(
                            label=f"🎯 {milestone:,} Commits",
                            value=f"{int(days)} days" if days != float('inf') else "Not projected",
                            delta=f"ETA: {format_date_ddmmyyyy(eta_date)}" if eta_date else None,
                            help=f"Progress: {progress:.1f}% ({total_contributions:,}/{milestone:,})",
                            border=True
                        )
                        
                        if progress > 0:
                            col.progress(min(100, progress) / 100, text=f"{progress:.1f}%")
            else:
                st.warning("No contributions found yet. Start contributing to see milestone predictions!")
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.stop()

else:
    st.info("ℹ️ ***Enter your GitHub username and token in the sidebar to get started.***")