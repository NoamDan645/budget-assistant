from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def normalize_expense_date(value: str | None) -> str:
    today = datetime.now(ZoneInfo("Asia/Jerusalem")).date()

    if value is None:
        return today.isoformat()

    relative_dates = {
        "היום": 0,
        "אתמול": 1,
        "שלשום": 2,
    }

    if value in relative_dates:
        days = relative_dates[value]
        return (today - timedelta(days=days)).isoformat()

    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError("התאריך חייב להיות בפורמט YYYY-MM-DD") from None

    if parsed.isoformat() != value:
        raise ValueError("התאריך חייב להיות בפורמט YYYY-MM-DD")

    return parsed.isoformat()

def normalize_summary_month(value: str | None) -> str | None:
    if value is None:
        return None

    if value == "החודש":
        today = datetime.now(ZoneInfo("Asia/Jerusalem")).date()
        return today.isoformat()[:7]

    try:
        parsed = date.fromisoformat(f"{value}-01")
    except ValueError:
        raise ValueError("החודש חייב להיות בפורמט YYYY-MM") from None

    if parsed.isoformat()[:7] != value:
        raise ValueError("החודש חייב להיות בפורמט YYYY-MM")

    return value