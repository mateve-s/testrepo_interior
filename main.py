import os
import base64
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Импортируем утилиты
from gigachat_utils import enhance_prompt_with_gigachat
from yandex_utils import YandexARTClient

app = FastAPI()

# Настраиваем шаблоны (папка templates должна быть рядом с main.py)
templates = Jinja2Templates(directory="templates")

# Инициализируем клиента Yandex ART
yandex_art_client = YandexARTClient()


class GenerateRequest(BaseModel):
    text: str
    style: Optional[str] = None
    room_size: Optional[str] = None
    lighting: Optional[str] = None


class GenerateResponse(BaseModel):
    original_text: str
    enhanced_prompt: str
    image_base64: str
    style: Optional[str] = None
    room_size: Optional[str] = None
    lighting: Optional[str] = None


def build_llm_input(request: GenerateRequest) -> str:
    return f"""
Преобразуй описание интерьера в детальный промпт для генерации изображения на английском языке.

Обязательно:
- сохрани смысл исходного запроса пользователя,
- учти выбранный стиль,
- учти размер комнаты для понимания масштаба,
- учти выбранный тип освещения,
- добавь детали про материалы, композицию, ракурс, атмосферу и качество изображения,
- итог должен быть одним готовым английским промптом для text-to-image модели,
- не добавляй пояснений, комментариев или markdown,
- только итоговый prompt.

Исходный запрос пользователя:
{request.text}

Выбранный стиль:
{request.style or "не указан"}

Размер комнаты:
{request.room_size or "не указан"}

Освещение:
{request.lighting or "не указано"}

Добавь к итоговому prompt характеристики уровня:
photorealistic, high detail, realistic materials, interior design photography, 8k
""".strip()


@app.post("/generate", response_model=GenerateResponse)
async def generate_interior(request: GenerateRequest):
    if not request.text or not request.text.strip():
        return JSONResponse(status_code=400, content={"message": "Text is required"})

    llm_input = build_llm_input(request)

    # 1. Улучшаем промпт через GigaChat
    try:
        enhanced_prompt = enhance_prompt_with_gigachat(llm_input)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"GigaChat error: {str(e)}"})

    # 2. Генерируем картинку через Yandex ART
    try:
        image_bytes = await yandex_art_client.generate_image(enhanced_prompt)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Yandex ART error: {str(e)}"})

    if image_bytes is None:
        return JSONResponse(status_code=500, content={"message": "Image generation failed (no image returned)"})

    # 3. Кодируем картинку в base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    return GenerateResponse(
        original_text=request.text,
        enhanced_prompt=enhanced_prompt,
        image_base64=image_base64,
        style=request.style,
        room_size=request.room_size,
        lighting=request.lighting
    )


@app.get("/")
async def root(request: Request):
    # Отдаём HTML-шаблон
    return templates.TemplateResponse("index_v2.html", {"request": request})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))  # по умолчанию 8002 для локальной разработки
    uvicorn.run(app, host="127.0.0.1", port=port)
