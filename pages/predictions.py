import streamlit as st
from streamlit import session_state as sst
from datetime import datetime
from utils.fetch_github_data import fetch_data_for_duration, fetch_user_data
from utils.process_github_data import analyze_contributions, process_user_data
from utils.util import predict_days_to_milestone, get_milestone_dates, format_date_ddmmyyyy
from utils.streamlit_ui import base_ui

def main():
    base_ui()

    if sst.username and sst.token and sst.button_pressed:                
        # Fetch data
        user_data = fetch_user_data(sst.username, sst.token)
        user_stats = process_user_data(user_data)
        created_at = datetime.strptime(user_stats.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
        created_at = created_at.strftime("%Y-%m-%d")

        today = datetime.now().strftime("%Y-%m-%d")
        current_year = datetime.now().year
        current_jan1st = datetime(current_year, 1, 1).strftime("%Y-%m-%d")
        last_jan1st = datetime(current_year-1, 1, 1).strftime("%Y-%m-%d")
        last_dec31st = datetime(current_year-1, 12, 31).strftime("%Y-%m-%d")

        # ------------- Last Year Contributions
        last_year_data_present = True
        from_date= last_jan1st# Date comes before Jan 1st. We use Jan 1st as starting date
        to_date= last_dec31st

        # Date comes between Jan 1st and Dec 31st. We use join date as start date
        if last_jan1st < created_at < last_dec31st: 
            from_date= created_at
        # Date comes after Dec 31st. Unable to calculate rate for last year
        elif created_at >= last_dec31st:
            last_year_data_present = False
        
            
        # If last year data is present
        if last_year_data_present:
            year_data = fetch_data_for_duration(
                sst.username, 
                sst.token,
                from_date= from_date,
                to_date= to_date
            )
            # Analyze only when data present
            whole_year_stats = analyze_contributions(year_data)

            # --- Get required stats ---
            contribution_rate_ly = whole_year_stats.get('contribution_rate', 0)
            # active_days_ly = whole_year_stats.get('active_days', 0)
        else:
            contribution_rate_ly = 0


        # -------------- Current Year Data
        from_date= created_at
        # Fetching current year data
        if current_jan1st >= created_at: # If joined before Jan 1st
            from_date= current_jan1st
        current_year_data = fetch_data_for_duration(
            sst.username, 
            sst.token,
            from_date= from_date,
            to_date= today
            )
        
        # Process current year data
        current_year_stats = analyze_contributions(current_year_data)
        
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
            if sst.user_token:
            
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
                        col.progress(100, text=f"{total_contributions}/{milestone}")
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
                            col.progress(progress / 100, text=f"{total_contributions}/{milestone}")
                            col.divider()
            else:
                st.info("Create GitHub Access Token to view these stats")



    else:
        st.info("ℹ️ ***Enter your GitHub username in the sidebar to see your stats.***")

if __name__ == "__main__":
    main()