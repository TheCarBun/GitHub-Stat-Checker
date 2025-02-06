from datetime import datetime
from dateutil.relativedelta import relativedelta

def format_duration(iso_date):
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

def format_date_ddmmyyyy(date):
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    formated_date = date_obj.strftime("%B {day}, %Y").replace("{day}", str(date_obj.day) + ("st" if date_obj.day in [1, 21, 31] else "nd" if date_obj.day == 2 else "rd" if date_obj.day == 3 else "th"))
    return formated_date

def is_less_than_2_months_old(iso_date):
    created_date = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    two_months_ago = datetime.now() - relativedelta(months=2)
    return created_date > two_months_ago

def format_iso_date(iso_date):
    dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%B {day}, %Y").replace("{day}", str(dt.day) + ("st" if dt.day in [1, 21, 31] else "nd" if dt.day == 2 else "rd" if dt.day == 3 else "th"))

def load_css() -> str:
    """
    Loads CSS stylesheet from local files.

    Returns:
    - str: The content of the CSS file.
    """
    try:
        with open('static/styles.css') as f:
            custom_css = f.read()
        return custom_css
    except FileNotFoundError:
        print("❗Error loading stylesheet: File not found.")
    except Exception as e:
        print(f"❗Error loading stylesheet: {e}")

