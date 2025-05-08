import asyncio
import logging
from dotenv import load_dotenv
from exchanges import binance, bybit, okx, bitget
from notifier import send_telegram_message
from db import init_db, is_new_listing

# Настройка логирования только в файл
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'  # кодироввка
)

# Загрузка переменных из .env
load_dotenv()

# Инициализация базы данных
init_db()

# Проверка одной биржи
async def check_exchange(exchange_func, exchange_name):
    try:
        logging.info(f"🔍 Проверка биржи: {exchange_name}")
        new_symbols = await exchange_func()
        for symbol in new_symbols:
            if is_new_listing(exchange_name, symbol):
                message = f"🆕 Новый листинг на {exchange_name}: {symbol}"
                logging.info(f"📢 {message}")
                await send_telegram_message(message)
            else:
                logging.debug(f"⏭ Уже в базе: {exchange_name} — {symbol}")
    except Exception as e:
        logging.error(f"Ошибка при проверке {exchange_name}: {e}")

# Главный цикл
async def main():
    while True:
        await asyncio.gather(
            check_exchange(binance.get_new_symbols, "Binance"),
            check_exchange(bybit.get_new_symbols, "Bybit"),
            check_exchange(okx.get_new_symbols, "OKX"),
            check_exchange(bitget.get_new_symbols, "Bitget"),
        )
        await asyncio.sleep(60)  # Ожидание 60 секунд до следующей проверки

if __name__ == "__main__":
    asyncio.run(main())
