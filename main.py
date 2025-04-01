import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from handlers.client_work import router
from services.logger_func import logger

dotenv_path = os.path.join(os.path.dirname(__file__), "config", ".env")
load_dotenv(dotenv_path)

token = os.getenv("TG_BOT_TOKEN")
if not token:
    raise ValueError(logger.error("BOT_TOKEN не найден в .env файле!"))

chat_id = os.getenv("TG_GROUP_ID")
if not chat_id:
    raise ValueError(logger.error("TG_GROUP_ID не найден в .env файле!"))

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("[main.py]: Бот запущен!")
    asyncio.run(main())
