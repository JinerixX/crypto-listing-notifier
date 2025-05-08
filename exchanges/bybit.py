import aiohttp

_last_symbols = set()

async def get_new_symbols():
    url = "https://api.bybit.com/v5/market/instruments-info?category=spot"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            symbols = {item["symbol"] for item in data["result"]["list"]}
    global _last_symbols
    new_listings = symbols - _last_symbols
    _last_symbols = symbols
    return new_listings
