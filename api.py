from fastapi import FastAPI
from pydantic import BaseModel

from agent import ApartmentAgent
from database import (
    create_database,
    add_test_apartments,
    update_complex_images
)


app = FastAPI(
    title="AI-агент по подбору квартир",
    description="API для поиска и сравнения квартир",
    version="1.0.0"
)

create_database()
add_test_apartments()
update_complex_images()


# Храним отдельного агента для каждого пользователя.
# Благодаря этому каждый пользователь сохраняет свой контекст диалога.
agents = {}


app = FastAPI(
    title="AI-агент по подбору квартир",
    description="API для поиска и сравнения квартир",
    version="1.0.0"
)


# Храним отдельного агента для каждого пользователя.
# Благодаря этому каждый пользователь сохраняет свой контекст диалога.
agents = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


def get_agent(session_id: str) -> ApartmentAgent:
    """Возвращает агента для текущей сессии."""

    if session_id not in agents:
        agents[session_id] = ApartmentAgent()

    return agents[session_id]


@app.get("/health")
def health_check():
    """Проверка работоспособности API."""

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):
    """Обрабатывает сообщение пользователя."""

    agent = get_agent(request.session_id)

    result = agent.process_message(
        request.message
    )

    return result