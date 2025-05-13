import os
import aiohttp
import asyncio
import logging

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    timeout = aiohttp.ClientTimeout(total=10)  # Установлен таймаут 10 секунд

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json={"chat_id": CHAT_ID, "text": text}) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logging.error(f"Ошибка Telegram API: статус {resp.status}, тело: {body}")
    except asyncio.TimeoutError:
        logging.error("⏱ Превышен таймаут при попытке отправить сообщение в Telegram.")
    except Exception as e:
        logging.error(f" Ошибка при отправке в Telegram: {e}")
