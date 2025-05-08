import aiohttp

_last_symbols = set()

async def get_new_symbols():
    url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            symbols = {item["instId"] for item in data["data"]}
    global _last_symbols
    new_listings = symbols - _last_symbols
    _last_symbols = symbols
    return new_listings
