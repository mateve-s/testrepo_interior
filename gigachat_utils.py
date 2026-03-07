import os
from gigachat import GigaChat

def enhance_prompt_with_gigachat(user_text: str) -> str:
    """
    Преобразует пользовательский запрос в детальный промпт для Yandex ART.
    """
    credentials = os.getenv("GIGACHAT_CREDENTIALS")
    if not credentials:
        raise ValueError("GIGACHAT_CREDENTIALS не найден в переменных окружения")

    with GigaChat(credentials=credentials, verify_ssl_certs=False) as giga:
        system_prompt = (
            "Ты — профессиональный дизайнер интерьеров. Твоя задача — преобразовать короткое описание интерьера от пользователя "
            "в максимально подробный промпт на **английском языке** для нейросети, генерирующей изображения (Yandex ART). "
            "Добавь детали: стиль (модерн, скандинавский, лофт...), освещение (мягкий солнечный свет, вечерний полумрак...), "
            "текстуры материалов (дерево, камень, текстиль...), атмосферу (уютно, минималистично, роскошно...). "
            "Используй ключевые слова вроде '8k', 'photorealistic', 'high quality'."
        )
        response = giga.chat(f"{system_prompt}\n\nЗапрос пользователя: {user_text}")
        return response.choices[0].message.content