import aiohttp

_last_symbols = set()

async def get_new_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            symbols = {s["symbol"] for s in data["symbols"] if s["status"] == "TRADING"}
    global _last_symbols
    new_listings = symbols - _last_symbols
    _last_symbols = symbols
    return new_listings
