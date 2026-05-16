import requests
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/crypto", tags=["crypto"])
templates = Jinja2Templates(directory="templates")

cache = {
    "prices": {},
    "last_update": 0
}

def get_all_prices_from_api():
    now = time.time()
    
    if cache["last_update"] and now - cache["last_update"] < 30:
        return cache["prices"]
    
    url = "https://api-web.tabdeal.org/r/plots/currencies/dynamic-info/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            currencies = data.get("currencies", {})
            
            result = {}
            for coin_name, coin_data in currencies.items():
                for currency, currency_data in coin_data.items():
                    symbol = f"{coin_name}/{currency}"
                    result[symbol] = {
                        "coin": coin_name,
                        "currency": currency,
                        "price": float(currency_data.get("price", 0)),
                        "high_24": float(currency_data.get("high_24", 0)),
                        "low_24": float(currency_data.get("low_24", 0)),
                        "change_24h": float(currency_data.get("change_percent_24", 0))
                    }
            
            cache["prices"] = result
            cache["last_update"] = now
            print(f"✅ Loaded {len(result)} currency pairs at {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return cache["prices"]

@router.get("/api/prices")
async def get_prices():
    data = get_all_prices_from_api()
    return {"success": True, "data": data, "count": len(data), "timestamp": cache["last_update"]}

@router.get("/api/history/{symbol}")
async def get_history(symbol: str):
    prices = get_all_prices_from_api()
    
    current_price = 0
    if symbol in prices:
        current_price = prices[symbol]["price"]
    
    history = []
    now = datetime.now()
    base_price = current_price if current_price > 0 else 1000
    
    for i in range(24):
        hour_ago = now - timedelta(hours=23-i)
        variation = 0.96 + (i * 0.002) + ((hash(symbol + str(i)) % 100) / 1000)
        price = base_price * variation
        
        history.append({
            "time": int(hour_ago.timestamp() * 1000),
            "value": round(price, 2)
        })
    
    return {"success": True, "symbol": symbol, "current_price": current_price, "history": history}

@router.get("", response_class=HTMLResponse)
async def crypto_page(request: Request):
    return templates.TemplateResponse("crypto.html", {"request": request})