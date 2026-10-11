from langchain_core.tools import tool
from date_utils import normalize_expense_date, normalize_summary_month
from budget_store import (
    add_expense,
    get_expenses ,
    get_category_summary,
    update_expense_category,
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

TOOLS = [
    record_expense,
    list_expenses,
    summarize_expenses,
    change_expense_category,

]