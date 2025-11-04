import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import aiohttp
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your tokens (will be set via environment variables)
TOKEN = os.environ.get("BOT_TOKEN")
SUNO_API_KEY = os.environ.get("SUNO_API_KEY")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "Hello! I am a music generation bot using Suno AI. 🎵\n\n"
        "Just send me a description of the song you want to hear, "
        "and I will create it for you!\n\n"
        "For example, try sending: 'Happy pop song about summer'"
    )
    await update.message.reply_text(welcome_text)

# Function to send request to Suno API
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
                logger.error(f"Suno API error: {result.get('msg')}")
                return None

# Text message handler (song description)
async def handle_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_prompt = update.message.text
    await update.message.reply_text("🎵 Got your request! Generating music... This will take a few minutes.")

    # Send request to Suno
    task_id = await generate_suno_song(user_prompt)

    if task_id:
        await update.message.reply_text(f"✅ Task created! ID: {task_id}. Please wait, I will send the result soon.")
    else:
        await update.message.reply_text("❌ Sorry, there was an error creating the song. Please try again later.")

# Main function
def main():
    # Create Telegram bot application
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_description))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
