from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.budget_store import init_db
from backend.expense_graph import create_graph
from backend.paths import FRONTEND_DIR


app = FastAPI(title="מנהל ההוצאות")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

init_db()
graph = create_graph()


MAX_MESSAGE_LENGTH = 2000


class ChatRequest(BaseModel):
    message: str = Field(max_length=MAX_MESSAGE_LENGTH)
    # When omitted, the server creates a random thread id and returns it.
    thread_id: str | None = Field(
        default=None,
        min_length=16,
        max_length=64,
        pattern=r"^[A-Za-z0-9-]+$",
    )


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

    thread_id = request.thread_id or str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    return {
        "reply": result["messages"][-1].content,
        "thread_id": thread_id,
    }
@app.get("/", response_class=FileResponse)
def home():
    return FileResponse(
        FRONTEND_DIR / "index.html",
        media_type="text/html",
    )
