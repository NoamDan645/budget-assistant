from langchain_core.tools import tool
from backend.date_utils import normalize_expense_date, normalize_summary_month
from backend.budget_store import (
    add_expense,
    get_expenses ,
    get_category_summary,
    update_expense_category,
    update_expense_details,
    save_monthly_budget,
    get_monthly_budget,
)

@tool
def record_expense(
    amount_agorot: int,
    description: str,
    category: str,
    expense_date: str | None = None,
) -> str:
    """שמור הוצאה חדשה.

    amount_agorot: סכום באגורות.
    description: תיאור קצר של ההוצאה.
    category: קטגוריה מתוך הרשימה המותרת.
    expense_date: YYYY-MM-DD, היום, אתמול או שלשום.
        אם לא צוין תאריך, השאר ריק כדי לשמור בתאריך היום.
    """
    saved_date = normalize_expense_date(expense_date)

    expense_id = add_expense(
        amount_agorot=amount_agorot,
        description=description,
        category=category,
        expense_date=saved_date,
    )

    return (
        f"הוצאה עם מזהה {expense_id} נשמרה "
        f"לתאריך {saved_date}"
    )

@tool
def list_expenses() -> list[dict]:
    """החזר את כל ההוצאות השמורות, מהחדשה לישנה."""
    return get_expenses()

def format_shekels(amount_agorot: int) -> str:
    shekels, agorot = divmod(amount_agorot, 100)
    return f"{shekels}.{agorot:02d}"

@tool
def summarize_expenses(month: str | None = None) -> str:
    """סכם הוצאות לפי קטגוריות.

    month: חודש בפורמט YYYY-MM או המילה החודש.
        ללא חודש, סכם את כל ההוצאות השמורות.
    """
    month = normalize_summary_month(month)
    summary = get_category_summary(month)

    title = (
        f"סיכום לחודש {month}:"
        if month
        else "סיכום של כל ההוצאות השמורות:"
    )
    lines = [title]

    if not summary:
        lines.append("לא נמצאו הוצאות לסיכום בטווח שנבחר.")

    for row in summary:
        amount = format_shekels(row["total_agorot"])
        lines.append(
            f"{row['category']}: {amount} ₪ "
            f"({row['expense_count']} הוצאות)"
        )

    total = sum(row["total_agorot"] for row in summary)
    lines.append(f"סך הכול: {format_shekels(total)} ₪")

    if month:
        undated_count = sum(
            expense["expense_date"] is None
            for expense in get_expenses()
        )

        if undated_count:
            lines.append(
                f"קיימות {undated_count} הוצאות ללא תאריך, "
                "שאינן כלולות בסיכום החודשי."
            )

    return "\n".join(lines)
@tool
def change_expense_category(
    expense_id: int,
    category: str,
) -> str:
    """שנה קטגוריה של הוצאה קיימת לפי המזהה שלה במסד הנתונים."""
    update_expense_category(
        expense_id=expense_id,
        category=category,
    )

    return (
        f"הקטגוריה של הוצאה עם מזהה {expense_id} "
        f"עודכנה ל-{category}"
    )
@tool
def edit_expense(
    expense_id: int,
    amount_agorot: int | None = None,
    expense_date: str | None = None,
) -> str:
    """תקן סכום או תאריך של הוצאה קיימת לפי המזהה שלה.

    amount_agorot: סכום חדש באגורות, רק אם התבקש שינוי סכום.
    expense_date: תאריך חדש, רק אם התבקש שינוי תאריך.
        אפשר YYYY-MM-DD, היום, אתמול או שלשום.
    """
    saved_date = (
        normalize_expense_date(expense_date)
        if expense_date is not None
        else None
    )

    update_expense_details(
        expense_id=expense_id,
        amount_agorot=amount_agorot,
        expense_date=saved_date,
    )

    changes = []

    if amount_agorot is not None:
        changes.append(f"סכום: {format_shekels(amount_agorot)} ₪")

    if saved_date is not None:
        changes.append(f"תאריך: {saved_date}")

    return (
        f"הוצאה עם מזהה {expense_id} עודכנה. "
        + ", ".join(changes)
    )

@tool
def set_monthly_budget(
    amount_agorot: int,
    month: str = "החודש",
) -> str:
    """הגדר או עדכן תקציב כולל לחודש מסוים.

    amount_agorot: התקציב באגורות.
    month: חודש בפורמט YYYY-MM או המילה החודש.
        אם לא צוין חודש, התקציב מיועד לחודש הנוכחי.
    """
    saved_month = normalize_summary_month(month)

    save_monthly_budget(
        month=saved_month,
        amount_agorot=amount_agorot,
    )

    return (
        f"התקציב לחודש {saved_month} נקבע על "
        f"{format_shekels(amount_agorot)} ₪"
    )
@tool
def budget_status(month: str = "החודש") -> str:
    """בדוק תקציב, הוצאות ויתרה לחודש מסוים.

    month: חודש בפורמט YYYY-MM או המילה החודש.
        ללא חודש מפורש, בדוק את החודש הנוכחי.
    """
    month = normalize_summary_month(month)
    budget = get_monthly_budget(month)

    if budget is None:
        return f"לא הוגדר תקציב לחודש {month}."

    summary = get_category_summary(month)
    spent = sum(row["total_agorot"] for row in summary)

    lines = [
        f"מצב התקציב לחודש {month}:",
        f"תקציב: {format_shekels(budget)} ₪",
        f"הוצאות: {format_shekels(spent)} ₪",
    ]

    if spent <= budget:
        remaining = budget - spent
        lines.append(
            f"נותרו: {format_shekels(remaining)} ₪"
        )
    else:
        overrun = spent - budget
        lines.append(
            f"חריגה מהתקציב: {format_shekels(overrun)} ₪"
        )

    undated_count = sum(
        expense["expense_date"] is None
        for expense in get_expenses()
    )

    if undated_count:
        lines.append(
            f"קיימות {undated_count} הוצאות ללא תאריך, "
            "שאינן כלולות בחישוב."
        )

    return "\n".join(lines)
TOOLS = [
    record_expense,
    list_expenses,
    summarize_expenses,
    change_expense_category,
    edit_expense,
    set_monthly_budget,
    budget_status,
]
