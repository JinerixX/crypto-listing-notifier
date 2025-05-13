import httpx
from .symbol import Symbol

async def get_new_symbols():
    spot_url = "https://api.bitget.com/api/spot/v1/public/products"
    futures_url = "https://api.bitget.com/api/mix/v1/market/contracts?productType=umcbl"

    async with httpx.AsyncClient() as client:
        spot_resp = await client.get(spot_url)
        futures_resp = await client.get(futures_url)

    spot_symbols = {s["symbol"].replace("-", "") for s in spot_resp.json().get("data", [])}
    futures_symbols = {s["symbol"].replace("-", "") for s in futures_resp.json().get("data", [])}

    all_symbols = spot_symbols | futures_symbols
    result = []

    for symbol in all_symbols:
        if symbol in spot_symbols and symbol in futures_symbols:
            result.append(Symbol(symbol, "Both"))
        elif symbol in spot_symbols:
            result.append(Symbol(symbol, "Spot"))
        else:
            result.append(Symbol(symbol, "Futures"))

    return result
