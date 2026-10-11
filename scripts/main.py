from bidi.algorithm import get_display
from langchain_core.messages import HumanMessage

from backend.budget_store import init_db
from backend.expense_graph import create_graph


def print_hebrew(text: str):
    print(get_display(text, base_dir="R"))


def main():
    init_db()
    graph = create_graph()

    config = {
        "configurable": {
            "thread_id": "budget-chat-1"
        }
    }

    print_hebrew("מנהל ההוצאות מוכן. לסיום כתוב יציאה.")

    while True:
        user_text = input("> ").strip()

        if user_text in {"יציאה", "exit"}:
            break

        if not user_text:
            continue

        result = graph.invoke(
            {"messages": [HumanMessage(content=user_text)]},
            config=config,
        )

        final_message = result["messages"][-1]
        print_hebrew(final_message.content)


if __name__ == "__main__":
    main()
