import os
import logging
from dotenv import load_dotenv
import aiohttp

logger = logging.getLogger(__name__)
chat_id = -int(os.getenv("TG_GROUP_ID"))
token = os.getenv("TG_BOT_TOKEN")

class TelegramBot:
    def __init__(self):
        if token is None or chat_id is None:
            dotenv_path = os.path.join(os.path.dirname(__file__), "..", "config", ".env")
            load_dotenv(dotenv_path)
            
            self.token = os.getenv("TG_BOT_TOKEN")
            self.chat_id = os.getenv("TG_GROUP_ID")
        else:
            self.token = token
            self.chat_id = chat_id

        if not self.token or not self.chat_id:
            logger.error("TG_BOT_TOKEN или TG_GROUP_ID не найдены в .env файле")
            raise ValueError("TG_BOT_TOKEN или TG_GROUP_ID не найдены в .env файле")

        self.base_url = f"https://api.telegram.org/bot{self.token}"
        logger.info(f"TelegramBot инициализирован с chat_id: {self.chat_id}")

    async def send_message(self, text: str) -> dict:
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": text
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    if not result.get("ok"):
                        logger.error(f"Ошибка отправки сообщения: {result}")
                        raise Exception(f"Ошибка Telegram API: {result.get('description', 'Неизвестная ошибка')}")
                    logger.info(f"Сообщение успешно отправлено: {text}")
                    return result
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение: {str(e)}")
            raise

