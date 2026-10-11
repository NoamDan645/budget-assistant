from uuid import uuid4

import httpx
from bidi.algorithm import get_display


def print_hebrew(text: str):
    print(get_display(text, base_dir="R"))


def main():
    thread_id = str(uuid4())

    print_hebrew("מנהל ההוצאות מוכן. לסיום כתוב יציאה.")

    with httpx.Client(
        base_url="http://127.0.0.1:8000",
        timeout=120.0,
    ) as client:
        while True:
            message = input("> ").strip()

            if message in {"יציאה", "exit"}:
                break

            if not message:
                continue

            try:
                response = client.post(
                    "/chat",
                    json={
                        "message": message,
                        "thread_id": thread_id,
                    },
                )

                response.raise_for_status()
                data = response.json()

                print_hebrew(data["reply"])

            except httpx.HTTPStatusError as error:
                print_hebrew(
                    "השרת החזיר שגיאה בקוד "
                    f"{error.response.status_code}."
                )

            except httpx.RequestError:
                print_hebrew(
                    "אירעה שגיאה בתקשורת עם השרת. "
                    "בדוק שהשרת פועל בטרמינל הראשון."
                )


if __name__ == "__main__":
    main()