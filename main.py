import asyncio
import logging
from dotenv import load_dotenv
from exchanges import binance, bybit, okx, bitget
from notifier import send_telegram_message
from db import init_db, is_new_listing, is_db_empty

# Настройка логирования в файл
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

# Загрузка переменных окружения
load_dotenv()

# Инициализация базы данных
init_db()

# Проверка одной биржи с уведомлением
async def check_exchange(exchange_func, exchange_name):
    try:
        logging.info(f"Проверка биржи: {exchange_name}")
        new_symbols = await exchange_func()
        for symbol in new_symbols:
            if is_new_listing(exchange_name, symbol.name, symbol.market_type):
                message = f"Монета {symbol.name} доступна для торговли на {exchange_name} ({symbol.market_type})"
                logging.info(message)
                await send_telegram_message(message)
            else:
                logging.debug(f"Пропущено (уже в базе): {exchange_name} — {symbol.name}")
    except Exception as e:
        logging.error(f"Ошибка при проверке {exchange_name}: {e}")

# Первичная загрузка без уведомлений
async def fill_db_silently(exchange_func, exchange_name):
    try:
        logging.info(f"Первичный запуск — заполняем базу: {exchange_name}")
        new_symbols = await exchange_func()
        for symbol in new_symbols:
            is_new_listing(exchange_name, symbol.name, symbol.market_type)
    except Exception as e:
        logging.exception(f"Ошибка при первичной инициализации {exchange_name}")

# Главный цикл
async def main():
    if is_db_empty():
        logging.info("База пуста — начинается первичная инициализация без уведомлений.")
        await asyncio.gather(
            fill_db_silently(binance.get_new_symbols, "Binance"),
            fill_db_silently(bybit.get_new_symbols, "Bybit"),
            fill_db_silently(okx.get_new_symbols, "OKX"),
            fill_db_silently(bitget.get_new_symbols, "Bitget"),
        )
        logging.info("Первичная инициализация завершена.")

    while True:
        await asyncio.gather(
            check_exchange(binance.get_new_symbols, "Binance"),
            check_exchange(bybit.get_new_symbols, "Bybit"),
            check_exchange(okx.get_new_symbols, "OKX"),
            check_exchange(bitget.get_new_symbols, "Bitget"),
        )
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())