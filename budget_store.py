import sqlite3
from contextlib import closing
from pathlib import Path
from categories import CATEGORIES
from date_utils import normalize_expense_date, normalize_summary_month
DB_PATH = Path(__file__).with_name("expenses.db")


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                amount_agorot INTEGER NOT NULL CHECK (amount_agorot > 0),
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(expenses)"
            )
        }

        if "expense_date" not in columns:
            connection.execute("""
                ALTER TABLE expenses
                ADD COLUMN expense_date TEXT
            """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS monthly_budgets (
                month TEXT PRIMARY KEY,
                amount_agorot INTEGER NOT NULL
                    CHECK (amount_agorot > 0)
            )
        """)
        connection.commit()

def add_expense(
    amount_agorot: int,
    description: str,
    category: str,
    expense_date: str | None = None,
) -> int:
    if type(amount_agorot) is not int or amount_agorot <= 0:
        raise ValueError("הסכום חייב להיות מספר שלם וחיובי של אגורות")

    description = description.strip()

    if not description:
        raise ValueError("חובה להזין תיאור להוצאה")

    if category not in CATEGORIES:
        raise ValueError("הקטגוריה אינה קיימת ברשימה")
    
    expense_date = normalize_expense_date(expense_date)
    
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses (
                amount_agorot,
                description,
                category,
                expense_date
            )
            VALUES (?, ?, ?, ?)
            """,
            (amount_agorot, description, category, expense_date),
        )
        connection.commit()
        return cursor.lastrowid

def get_expenses() -> list[dict]:
    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute("""
            SELECT id, amount_agorot, description, category, expense_date
            FROM expenses
            ORDER BY id DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

def get_category_summary(month: str | None = None) -> list[dict]:
    month = normalize_summary_month(month)

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute(
            """
            SELECT
                category,
                SUM(amount_agorot) AS total_agorot,
                COUNT(*) AS expense_count
            FROM expenses
            WHERE (
                ? IS NULL
                OR substr(expense_date, 1, 7) = ?
            )
            GROUP BY category
            ORDER BY total_agorot DESC
            """,
            (month, month),
        )

        return [dict(row) for row in cursor.fetchall()]

def update_expense_category(
    expense_id: int,
    category: str,
) -> None:
    if type(expense_id) is not int or expense_id <= 0:
        raise ValueError("מזהה ההוצאה חייב להיות מספר שלם וחיובי")

    if category not in CATEGORIES:
        raise ValueError("הקטגוריה אינה קיימת ברשימה")

    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            """
            UPDATE expenses
            SET category = ?
            WHERE id = ?
            """,
            (category, expense_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"לא נמצאה הוצאה עם מזהה {expense_id}")

        connection.commit()

def update_expense_details(
    expense_id: int,
    amount_agorot: int | None = None,
    expense_date: str | None = None,
) -> None:
    if type(expense_id) is not int or expense_id <= 0:
        raise ValueError("מזהה ההוצאה חייב להיות מספר שלם וחיובי")

    if amount_agorot is None and expense_date is None:
        raise ValueError("יש לציין סכום או תאריך לתיקון")

    if amount_agorot is not None:
        if type(amount_agorot) is not int or amount_agorot <= 0:
            raise ValueError("הסכום חייב להיות מספר שלם וחיובי של אגורות")

    if expense_date is not None:
        expense_date = normalize_expense_date(expense_date)

    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.execute(
            """
            UPDATE expenses
            SET
                amount_agorot = COALESCE(?, amount_agorot),
                expense_date = COALESCE(?, expense_date)
            WHERE id = ?
            """,
            (amount_agorot, expense_date, expense_id),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"לא נמצאה הוצאה עם מזהה {expense_id}")

        connection.commit()

def save_monthly_budget(month: str, amount_agorot: int) -> None:
    month = normalize_summary_month(month)

    if month is None:
        raise ValueError("יש לציין חודש לתקציב")

    if type(amount_agorot) is not int or amount_agorot <= 0:
        raise ValueError("התקציב חייב להיות מספר שלם וחיובי של אגורות")

    with closing(sqlite3.connect(DB_PATH)) as connection:
        connection.execute(
            """
            INSERT INTO monthly_budgets (month, amount_agorot)
            VALUES (?, ?)
            ON CONFLICT(month)
            DO UPDATE SET amount_agorot = excluded.amount_agorot
            """,
            (month, amount_agorot),
        )
        connection.commit()

def get_monthly_budget(month: str) -> int | None:
    month = normalize_summary_month(month)

    if month is None:
        raise ValueError("יש לציין חודש לבדיקת התקציב")

    with closing(sqlite3.connect(DB_PATH)) as connection:
        row = connection.execute(
            """
            SELECT amount_agorot
            FROM monthly_budgets
            WHERE month = ?
            """,
            (month,),
        ).fetchone()

        return row[0] if row is not None else None