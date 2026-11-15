from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI, APIConnectionError

app = FastAPI(
    title="LLM API",
    description="Учебное приложение с подключением к языковой модели",
    version="0.1.0",
)
client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)

class GenerateRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=200)
    temperature: float = Field(default=0.3, ge=0.0, le=1.0)

class StudyPlan(BaseModel):
    title: str
    description: str
    type: str
    steps: list[str] = Field(min_length=1, max_length=10)
    estimated_hours: int = Field(ge=1, le=100)

class GenerateResponse(BaseModel):
    topic: str
    temperature: float
    plan: StudyPlan


@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    try:
        completion = client.chat.completions.create(
            model="qwen3:1.7b",
            messages=[
                {
                    "role": "system",
                    "content": "Ты помощник, который составляет краткие учебные планы.",
                },
                {
                    "role": "user",
                    "content": f"Составь учебный план на русском языке по теме: {request.topic}",
                },
            ],
            temperature=request.temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "study_plan",
                    "schema": StudyPlan.model_json_schema(),
                },
            },
        )

        model_answer = completion.choices[0].message.content
        plan = StudyPlan.model_validate_json(model_answer)

        return {
            "topic": request.topic,
            "temperature": request.temperature,
            "plan": plan,
        }

    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Ollama недоступна. Запустите Ollama и повторите запрос.",
        )

    except ValidationError:
        raise HTTPException(
            status_code=502,
            detail="Модель вернула данные неправильной структуры.",
        )
