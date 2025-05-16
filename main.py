import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

from exchanges import binance, bybit, okx, bitget
from notifier import send_telegram_message
from db import init_db, is_new_listing, is_db_empty


# ─────────────────────── 1. логирование (файл + консоль) ──────────────────────
LOG_FMT  = "[%(asctime)s] %(levelname)s - %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter(LOG_FMT, DATE_FMT))
root_logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(LOG_FMT, DATE_FMT))
root_logger.addHandler(console_handler)

logging.getLogger("httpx").setLevel(logging.WARNING)
# ───────────────────────────────────────────────────────────────────────────────

# ───────────────────── 2. переменные окружения (.env) ─────────────────────────
load_dotenv()

REQUIRED_KEYS = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
if missing:
    msg = (
        "❌  Программа остановлена: отсутствуют ключи "
        f"{', '.join(missing)} в переменных окружения"
    )
    logging.error(msg)
    print(msg, file=sys.stderr)
    sys.exit(1)
# ───────────────────────────────────────────────────────────────────────────────

# ───────────────────── 3. инициализация базы данных ───────────────────────────
init_db()
# ───────────────────────────────────────────────────────────────────────────────


# ───────────── 4. универсальный простой асинхронный retry-цик� ────────────────
async def retry_until_success(coro, *, name: str, delay: int = 5):
    """
    Выполняет coroutine `coro()` до первого успешного завершения.
    При исключении пишет WARNING, ждёт `delay` секунд и повторяет.
    """
    attempt = 1
    while True:
        try:
            return await coro()
        except Exception as exc:
            logging.warning(
                f"[{name}] попытка #{attempt} не удалась: {exc}. "
                f"Повтор через {delay} с."
            )
            attempt += 1
            await asyncio.sleep(delay)
# ───────────────────────────────────────────────────────────────────────────────


# ────────────────── 5. функции работы с биржами ───────────────────────────────
async def check_exchange(exchange_func, exchange_name):
    """
    Периодический опрос биржи в рабочем цикле. Ошибки не останавливают
    всё приложение — пишем в лог и ждём следующей итерации main-loop.
    """
    try:
        logging.info(f"Проверка биржи: {exchange_name}")
        new_symbols = await exchange_func()
        for symbol in new_symbols:
            if is_new_listing(exchange_name, symbol.name, symbol.market_type):
                msg = (
                    f"Монета {symbol.name} доступна для торговли "
                    f"на {exchange_name} ({symbol.market_type})"
                )
                logging.info(msg)
                await send_telegram_message(msg)
    except Exception as exc:
        logging.error(f"Ошибка при проверке {exchange_name}: {exc}")


async def fill_db_silently(exchange_func, exchange_name):
    """
    Первичный ввод данных в БД.  Использует бесконечный retry-цикл
    до успешного ответа биржи.
    """
    logging.info(f"Первичный запуск — заполняем базу: {exchange_name}")
    new_symbols = await retry_until_success(exchange_func, name=exchange_name)
    for symbol in new_symbols:
        is_new_listing(exchange_name, symbol.name, symbol.market_type)
    logging.info(f"[{exchange_name}] первичная инициализация успешна.")
# ───────────────────────────────────────────────────────────────────────────────


# ─────────────────────── 6. главный асинхронный цикл ──────────────────────────
async def main():
    if is_db_empty():
        logging.info("База пуста — начинается первичная инициализация.")
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
# ───────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    asyncio.run(main())
