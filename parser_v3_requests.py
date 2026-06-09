import requests
import json
import re
from datetime import datetime
import time

def find_ozon_position(query: str, sku: str):
    url = "https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2"
    
    params = {
        "url": f"/search/?text={query}&sorting=score",
        "layout_container": "categorySearchMegapagination",
        "layout_page_index": "1"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Referer": "https://www.ozon.ru/",
    }
    
    session = requests.Session()
    session.get("https://www.ozon.ru/", headers=headers, timeout=15)
    time.sleep(2)
    
    response = session.get(url, params=params, headers=headers, timeout=15)
    data = response.json()
    
    # widgetStates всегда пустой - API требует авторизацию или особые заголовки
    widget_states = data.get("widgetStates", {})
    print("Ключи widgetStates:", list(widget_states.keys())[:5])  # всегда []
    
    return {
        "query": query,
        "sku": str(sku),
        "position": "not_found",
        "page": 1,
        "total_checked": 0,
        "timestamp": datetime.now().isoformat()
    }

def main():
    test_cases = [
        {"query": "наушники", "sku": "1403391454"},
        {"query": "телефон", "sku": "4189905294"},
        {"query": "ноутбук", "sku": "2561680703"}
    ]
    for test in test_cases:
        result = find_ozon_position(test['query'], test['sku'])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        time.sleep(30)

if __name__ == "__main__":
    main()