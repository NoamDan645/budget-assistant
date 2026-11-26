# Budget Assistant

A conversational personal expense manager in Hebrew, built as a learning project with **Python, LangChain and LangGraph**. · [עברית](README.he.md)

You tell the assistant what you spent in plain language, and it records the expense, assigns a category, and answers questions about your spending.

## Features

- **Log expenses by chatting**, including the date of each expense
- **Automatic categorization** into fixed categories (groceries, restaurants, clothing, transport, housing, health, leisure, studies, other)
- **Fix a category or edit an expense** after it was recorded
- **Monthly budgets** and budget status
- **Overall and monthly summaries**

Expenses and budgets are stored in **SQLite**. Conversation memory is kept while the program is running.

## How it works

A LangGraph agent backed by an OpenAI model decides which tool to call for each message. The tools (`record_expense`, `list_expenses`, `summarize_expenses`, `change_expense_category`, `edit_expense`, `set_monthly_budget`, `budget_status`) read and write the SQLite database. A FastAPI server exposes the agent over HTTP (`POST /chat`, `GET /health`) and serves a Hebrew web UI.

## Project structure

- `backend/`: the server, the agent, its tools and database access
- `frontend/`: the Hebrew web UI
- `data/expenses.db`: expenses and budgets (the data folder is not committed to Git)
- `scripts/`: terminal chat programs
- `.env`: API keys, in the project root

## Getting started

Run all commands from the project root (`budget-assistant`).

Install the dependencies inside a virtual environment:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your OpenAI API key.

Start the development server:

```powershell
python -m uvicorn backend.server:app --reload
```

Open the app at http://127.0.0.1:8000.
The interactive API docs are at http://127.0.0.1:8000/docs.

Run the terminal client (in a second terminal, while the server is running):

```powershell
python -m scripts.client
```

Chat with the agent directly in the terminal, without the server:

```powershell
python -m scripts.main
```

The server keeps conversation memory for as long as it is running. Data is stored in SQLite.

## Tech stack

Python · LangChain · LangGraph · OpenAI · FastAPI · SQLite · HTML/JavaScript
