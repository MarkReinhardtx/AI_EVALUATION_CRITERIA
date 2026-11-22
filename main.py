from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from openai import APIConnectionError, OpenAI
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, SessionLocal, engine


class Message(Base):
    __tablename__ = "messages"

    # Уникальный номер сообщения
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Автор сообщения: user или assistant
    role: Mapped[str]

    # Текст сообщения
    content: Mapped[str]


# Создаём таблицы, если их ещё нет
Base.metadata.create_all(engine)


# =========================
# 3. МОДЕЛИ ЗАПРОСОВ И ОТВЕТОВ
# =========================

class GenerateRequest(BaseModel):
    post_request: str = Field(
        min_length=2,
        max_length=300,
    )

class FAQDescription(BaseModel):
        description: str = Field(min_length=1,
        max_length=1000)

class GenerateResponseFAQ(BaseModel):
    temperature: float
    source: str
    info: FAQDescription

class GenerateResponse(BaseModel):
    temperature: float
    source: str
    answer: str = Field(min_length=1,
        max_length=10000)




# =========================
# 4. НАСТРОЙКА FASTAPI И OLLAMA
# =========================

app = FastAPI(
    title="LLM API",
    description=(
        "Учебное приложение с подключением "
        "к языковой модели"
    ),
    version="0.1.0",
)


client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama",
)


# =========================
# 5. ГОТОВЫЕ ОТВЕТЫ FAQ
# =========================

FAQ_ANSWERS = {
    "достоевский": FAQDescription(
        description=(
            "Фёдор Михайлович Достоевский — русский писатель, "
            "автор произведений «Преступление и наказание» "
            "и «Братья Карамазовы»."
        )
    ),
    "пушкин": FAQDescription(
        description=(
            "Александр Серге́евич Пушкин (26 мая [6 июня] 1799, Москва — 29 января [10 февраля] 1837, Санкт-Петербург) — русский поэт, драматург и прозаик, заложивший основы русского реалистического направления, литературный критик и теоретик литературы, историк, публицист, журналист, редактор и издатель. "

        )
    ),
}



# =========================
# 6. РАБОТА С ИСТОРИЕЙ
# =========================

def load_history() -> list[dict[str, str]]:
    with SessionLocal() as db:
        result = db.scalars(
            select(Message)
            .order_by(Message.id.desc())
            .limit(10)
        )

        messages = list(result)

    messages.reverse()

    history = []

    for message in messages:
        history.append({
            "role": message.role,
            "content": message.content,
        })

    return history


def save_messages(
    user_text: str,
    assistant_text: str,
) -> None:
    """Сохраняет вопрос пользователя и ответ Ollama."""

    user_message = Message(
        role="user",
        content=user_text,
    )

    assistant_message = Message(
        role="assistant",
        content=assistant_text,
    )

    with SessionLocal() as db:
        db.add_all([
            user_message,
            assistant_message,
        ])

        db.commit()


# =========================
# 7. ENDPOINT: ГЛАВНАЯ СТРАНИЦА
# =========================

@app.get("/")
def check():
    return {
        "message": "Здарова",
    }


# =========================
# 8. ENDPOINT: СОЗДАНИЕ ДИАЛОГА
# ========================


# =========================
# 9. ENDPOINT: ОТПРАВКА СООБЩЕНИЯ
# =========================

@app.post("/dialog",
    response_model=GenerateResponseFAQ | GenerateResponse,
)
def send_message(
    request: GenerateRequest,

        temperature: float = Header(
        default=0.3,
        ge=0.0,
        le=1.0,
        alias="temperature",
    ),
):


    normalized_request = (
        request.post_request.strip().casefold()
    )

    faq_phrase = (
        "Расскажи мне про писателя"
    ).casefold()

    # =========================
    # ПРОВЕРКА FAQ
    # =========================

    if faq_phrase in normalized_request:
        for autor_name, faq_answer in FAQ_ANSWERS.items():
            if autor_name in normalized_request:

                return {
                    "temperature": temperature,
                    "source": "FAQ",
                    "info": faq_answer,
                    }


    history = load_history()

    # =========================
    # ОБРАЩЕНИЕ К OLLAMA
    # =========================

    try:
        completion = client.chat.completions.create(
            model="qwen3.5:4b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты помощник по русской литературе. "
                        "Отвечай только на русском языке. "
                        "Не придумывай факты. "
                        "Пиши обычным текстом без Markdown. "
                        "Не используй символы #, *, списки и заголовки. "
                        "Не делай переносы строк. "
                        "Ответ оформляй одним связным абзацем."
                    ),
                },

                # Предыдущие сообщения из PostgreSQL
                *history,

                # Новый вопрос пользователя
                {
                    "role": "user",
                    "content": request.post_request,
                },
            ],

            extra_body={
                "reasoning_effort": "none",
            },

            temperature=temperature,
            max_tokens=10000,


        )

        # Получаем текст ответа Ollama
        model_answer = (
            completion.choices[0].message.content
        )

        if model_answer is None or not model_answer.strip():
            raise HTTPException(
                status_code=502,
                detail="Ollama вернула пустой ответ"
            )

        # Сохраняем вопрос и ответ в PostgreSQL
        save_messages(
            user_text=request.post_request,
            assistant_text=model_answer,
        )

        return {
            "temperature": temperature,
            "source": "Ollama",
            "answer": model_answer
        }

    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ollama недоступна. "
                "Запустите Ollama и повторите запрос."
            ),
        )