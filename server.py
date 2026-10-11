from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from budget_store import init_db
from expense_graph import create_graph


app = FastAPI(title="מנהל ההוצאות")

init_db()
graph = create_graph()


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "budget-chat-1"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="ההודעה אינה יכולה להיות ריקה",
        )

    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    return {
        "reply": result["messages"][-1].content,
        "thread_id": request.thread_id,
    }