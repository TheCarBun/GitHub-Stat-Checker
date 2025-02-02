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

def is_less_than_2_months_old(iso_date):
    created_date = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    two_months_ago = datetime.now() - relativedelta(months=2)
    return created_date > two_months_ago

def format_date(iso_date):
    dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime("%B {day}, %Y").replace("{day}", str(dt.day) + ("st" if dt.day in [1, 21, 31] else "nd" if dt.day == 2 else "rd" if dt.day == 3 else "th"))
