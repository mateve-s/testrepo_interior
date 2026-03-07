import os
from yandex_ai_studio_sdk import AIStudio

class YandexARTClient:
    """
    Клиент для генерации изображений через YandexART.
    Использует официальный SDK Яндекс AI Studio.
    Полностью соответствует примеру из документации:
    https://aistudio.yandex.ru/docs/ru/ai-studio/operations/generation/yandexart-request.html
    """
    
    def __init__(self):
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.api_key = os.getenv("YANDEX_API_KEY")
        
        if not self.folder_id or not self.api_key:
            raise ValueError("YANDEX_FOLDER_ID и YANDEX_API_KEY должны быть указаны в .env")
        
        # Инициализируем SDK ровно как в документации
        self.sdk = AIStudio(
            folder_id=self.folder_id,
            auth=self.api_key,  # API-ключ сервисного аккаунта
        )
        
        # Получаем модель генерации изображений
        self.model = self.sdk.models.image_generation("yandex-art")
        
        # Можно настроить параметры по умолчанию (опционально)
        self.model = self.model.configure(
            width_ratio=1,  # соотношение сторон
            height_ratio=1,
            seed=None  # None = случайный seed
        )
    
    def generate_image_sync(self, prompt: str) -> bytes:
        """
        Генерирует изображение по промпту.
        
        Args:
            prompt: текстовое описание на английском
            
        Returns:
            bytes: изображение в формате JPEG (как в документации)
        """
        # Запускаем генерацию и ждём результат
        # Это прямая аналогия с примером из документации:
        # operation = model.run_deferred(message1)
        # result = operation.wait()
        operation = self.model.run_deferred(prompt)
        result = operation.wait()
        
        # В документации result.image_bytes содержит готовое изображение
        return result.image_bytes
    
    async def generate_image(self, prompt: str) -> bytes:
        """
        Асинхронная обёртка для FastAPI.
        """
        import asyncio
        return await asyncio.to_thread(self.generate_image_sync, prompt)