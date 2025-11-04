import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваши токены (будут заданы через переменные окружения)
TOKEN = os.environ.get("BOT_TOKEN")
SUNO_API_KEY = os.environ.get("SUNO_API_KEY")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "Привет! Я бот для генерации музыки с помощью Suno AI. ??\n\n"
        "Просто напиши мне описание песни, которую ты хочешь услышать, "
        "и я создам ее для тебя!\n\n"
        "Например, попробуй отправить: 'Веселая поп-песня о лете'"
    )
    await update.message.reply_text(welcome_text)

# Функция для отправки запроса к Suno API
async def generate_suno_song(prompt: str):
    api_url = "https://api.sunoapi.org/api/v1/generate"
    headers = {
        'Authorization': f'Bearer {SUNO_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "prompt": prompt,
        "customMode": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=data) as response:
            result = await response.json()
            if result.get('code') == 200:
                return result['data']['taskId']
            else:
                logger.error(f"Ошибка Suno API: {result.get('msg')}")
                return None

# Обработчик текстовых сообщений
async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text
    await update.message.reply_text("?? Принял твой запрос! Генерирую музыку... Это займет несколько минут.")

    # Отправляем запрос в Suno
    task_id = await generate_suno_song(user_prompt)

    if task_id:
        await update.message.reply_text(f"? Задача создана! ID: {task_id}. Ожидайте, скоро пришлю результат.")
        # Здесь будет код для проверки статуса и получения песни
    else:
        await update.message.reply_text("? К сожалению, при создании песни произошла ошибка. Попробуй еще раз позже.")

# Основная функция
def main():
    # Создаем приложение Telegram бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()