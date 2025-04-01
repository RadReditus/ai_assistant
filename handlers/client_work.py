import logging
import random
import io
import os
import subprocess
import speech_recognition as sr
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.gpt import get_gpt_response
from services.config import HELLO_PROMPT, PHONE_PROMPT, COUNTRY_PROMPT
from services.sheet_worker import SheetWorker
from services.logger_func import logger
from services.manage_msgs import TelegramBot


handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_OGG_PATH = os.path.join(BASE_DIR, "temp_audio.ogg")
TEMP_WAV_PATH = os.path.join(BASE_DIR, "temp_audio.wav")

if not os.access(BASE_DIR, os.W_OK):
    logger.error(f"Нет прав на запись в директорию: {BASE_DIR}")
    raise PermissionError(f"Нет прав на запись в директорию: {BASE_DIR}")

router = Router()

class ClientForm(StatesGroup):
    name = State()
    phone = State()
    country = State()

async def converting_audio_to_text(bot: Bot, message: types.Message) -> str | None:
    try:
        if not message.voice:
            raise ValueError("Не найдено голосовое сообщение")

        file_id = message.voice.file_id
        logger.info(f"Получен file_id: {file_id}")

        file = await bot.get_file(file_id)
        file_path = file.file_path
        if not file_path:
            raise ValueError("file_path пустой")

        audio_bytes = io.BytesIO()
        await bot.download_file(file_path, audio_bytes)
        logger.info(f"Файл скачан, размер: {audio_bytes.getbuffer().nbytes} байт")

        with open(TEMP_OGG_PATH, "wb") as f:
            f.write(audio_bytes.getvalue())
        logger.info(f"Аудиофайл сохранён: {TEMP_OGG_PATH}")

        result = subprocess.run(["ffmpeg", "-i", TEMP_OGG_PATH, "-ar", "16000", "-ac", "1", TEMP_WAV_PATH], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Ошибка при конвертации в WAV: {result.stderr}")
            raise FileNotFoundError("Ошибка при конвертации в WAV")

        recognizer = sr.Recognizer()
        with sr.AudioFile(TEMP_WAV_PATH) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language="ru-RU")
        logger.info(f"Распознанный текст: {text}")

        os.remove(TEMP_OGG_PATH)
        os.remove(TEMP_WAV_PATH)
        logger.info("Временные файлы удалены")

        return text

    except Exception as e:
        logger.error(f"Ошибка при обработке аудиофайла: {str(e)}")
        for temp_file in [TEMP_OGG_PATH, TEMP_WAV_PATH]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"Временный файл удалён после ошибки: {temp_file}")
        return None

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    response = get_gpt_response(HELLO_PROMPT, "")  

    if response:
        await message.answer(response)
    else:
        await message.answer("Привет! Как вас зовут полностью?")

    await state.set_state(ClientForm.name)

@router.message(ClientForm.name)
async def process_name(message: types.Message, state: FSMContext, bot: Bot):
    if message.voice or message.audio:
        text = await converting_audio_to_text(bot, message)
        if text:
            await state.update_data(name=text)  
        else:
            await message.answer("Не удалось распознать голосовое сообщение. Попробуйте снова.")
            return
    else:
        name = message.text
        if not name.strip(): 
            await message.answer("Пожалуйста, введите ваше имя.")
            return
        await state.update_data(name=name)

    data = await state.get_data() 
    name = data.get('name')  

    if name:
        phone_prompt = get_gpt_response(PHONE_PROMPT, name)
        await message.answer(phone_prompt)
        await state.set_state(ClientForm.phone)
    else:
        await message.answer("Имя не было введено. Попробуйте снова.")

@router.message(ClientForm.phone)
async def process_phone(message: types.Message, state: FSMContext, bot: Bot):
    if message.voice or message.audio:
        text = await converting_audio_to_text(bot, message)
        if text:
            await state.update_data(phone=text)  
        else:
            await message.answer("Не удалось распознать голосовое сообщение. Попробуйте снова.")
            return
    else:
        phone = message.text.strip()
        if not phone:
            await message.answer("Пожалуйста, введите ваш номер телефона.")
            return
        await state.update_data(phone=phone)

    data = await state.get_data()  
    phone = data.get('phone')  

    if phone:
        country_prompt = get_gpt_response(COUNTRY_PROMPT, phone)
        await message.answer(country_prompt)
        await state.set_state(ClientForm.country)
    else:
        await message.answer("Номер телефона не был введен. Попробуйте снова.")

@router.message(ClientForm.country)
async def process_country(message: types.Message, state: FSMContext, bot: Bot):
    if message.voice or message.audio:
        text = await converting_audio_to_text(bot, message)
        if text:
            await state.update_data(country=text)
        else:
            await message.answer("Не удалось распознать голосовое сообщение. Попробуйте снова.")
            return
    else:
        country = message.text
        if not country.strip():
            await message.answer("Пожалуйста, введите страну.")
            return
        await state.update_data(country=country)

    data = await state.get_data()
    name = data.get('name')
    phone = data.get('phone')
    country = data.get('country')

    try:
        sheet_worker = SheetWorker()
        sheet_worker.write_info_to_sheets(name, phone, country)
        bot_sender = TelegramBot()
        await bot_sender.send_message(logger.info(f"Новый лид в гугл таблице \n {name} \n {phone} \n {country}"))
    except Exception as e:
        await message.answer(logger.error(f"Произошла ошибка при записи данных: {str(e)}"))
        return

    final_messages = [
        "Спасибо! Вот что у нас получилось:",
        "Отлично, вот ваши данные:",
        "Готово! Давайте посмотрим, что у нас:"
    ]
    await message.answer(
        f"{random.choice(final_messages)}\n"
        f"1 - {name}\n"
        f"2 - {phone}\n"
        f"3 - {country}"
    )
    await state.clear()
