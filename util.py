from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def format_duration(iso_date:str) -> str:
    """
    Formats the duration from the given ISO date to the current date in years, months, and days.

    Args:
        iso_date (str): The ISO formatted date string (e.g., "2023-02-07T12:34:56Z").

    Returns:
        str: The formatted duration string (e.g., "2 years 3 months 5 days").
    """
    created_at = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.now()
    delta = now - created_at

    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30

    parts = []
    if years:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")

    return " ".join(parts) if parts else "0 days"

def format_date_ddmmyyyy(date:str) -> str:
    """
    Formats a date string from 'YYYY-MM-DD' to 'DDth MMM, YYYY'.

    Args:
        date (str): The date string in 'YYYY-MM-DD' format.

    Returns:
        str: The formatted date string (e.g., "7th Feb, 2025").
    """
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    formated_date = date_obj.strftime("{day} %b, %Y").replace("{day}", str(date_obj.day) + ("st" if date_obj.day in [1, 21, 31] else "nd" if date_obj.day in [2, 22] else "rd" if date_obj.day in [3, 23] else "th"))
    return formated_date

def format_iso_date(iso_date:str) -> str:
    """
    Formats an ISO date string to 'DDth MMM, YYYY'.

    Args:
        iso_date (str): The ISO date string (e.g., "2023-02-07T12:34:56Z").

    Returns:
        str: The formatted date string (e.g., "7th Feb, 202
    """
    dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("{day} %b, %Y").replace("{day}", str(dt.day) + ("st" if dt.day in [1, 21, 31] else "nd" if dt.day  in [2, 22] else "rd" if dt.day in [3, 23] else "th"))

def is_less_than_2_months_old(iso_date:str) -> bool:
    """
    Checks if the given ISO date is less than 2 months old from the current date.

    Args:
        iso_date (str): The ISO formatted date string (e.g., "2023-02-07T12:34:56Z").

    Returns:
        bool: True if the date is less than 2 months old, False otherwise.
    """
    created_date = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    two_months_ago = datetime.now() - relativedelta(months=2)
    return created_date > two_months_ago

def load_css() -> str:
    """
    Loads CSS stylesheet from local files.

    Returns:
        str: The content of the CSS file.

    Raises:
        FileNotFoundError: If the CSS file is not found.
        Exception: For any other exceptions that occur during file reading.
    """
    try:
        with open('static/styles.css') as f:
            custom_css = f.read()
        return custom_css
    except FileNotFoundError:
        print("❗Error loading stylesheet: File not found.")
    except Exception as e:
        print(f"❗Error loading stylesheet: {e}")

def predict_days_to_milestone(current_contributions, milestone, contribution_rate):
    """Predicts how many days are required to reach the milestone."""
    if contribution_rate <= 0:
        return float('inf')  # Cannot reach milestone with zero contributions per day
    remaining_contributions = milestone - current_contributions
    if remaining_contributions <= 0:
        return 0  # Already reached
    days_required = remaining_contributions / contribution_rate
    return days_required


def get_milestone_dates(milestones, contributions, total_contributions, contribution_rate):
    """
    Finds the exact dates when milestones were achieved from GraphQL data and predicts future ones.

    Args:
    - milestones (list): List of milestone commit targets.
    - contributions (list): Contribution data from GraphQL (weeks > contributionDays).
    - total_contributions (int): Current total contributions.
    - contribution_rate (float): Daily contribution rate.

    Returns:
    - dict: Milestone predictions with exact dates (if achieved) and estimated dates (if not achieved).
    """
    milestone_dates = {}
    cumulative_contributions = 0

    # --- Traverse through contributions to find exact dates ---
    for week in contributions:
        for day in week["contributionDays"]:
            contribution_count = day["contributionCount"]
            date = day["date"]

            if contribution_count > 0:
                cumulative_contributions += contribution_count

                # If a milestone is reached, store its exact date
                for milestone in milestones:
                    if milestone not in milestone_dates and cumulative_contributions >= milestone:
                        milestone_dates[milestone] = date

    # --- Predict future milestone dates ---
    today = datetime.now()
    if contribution_rate > 0:
        for milestone in milestones:
            if milestone not in milestone_dates:  # Only predict if not already achieved
                remaining_commits = milestone - total_contributions
                days_to_milestone = remaining_commits / contribution_rate
                milestone_dates[milestone] = (today + timedelta(days=days_to_milestone)).strftime("%Y-%m-%d")
    else:
        for milestone in milestones:
            if milestone not in milestone_dates:
                milestone_dates[milestone] = "Not achievable"

    return milestone_dates

