import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import time

async def find_ozon_position(query, sku):
    url = f"https://www.ozon.ru/search/?text={query}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print(f"Открываю: {url}")
        await page.goto(url, timeout=30000)
        await page.wait_for_timeout(5000)
        try:
            cards = await page.query_selector_all('[data-sku]')
            position = 1
            for card in cards:
                sku_value = await card.get_attribute('data-sku')
                if sku_value == str(sku):
                    await browser.close()
                    return {"query": query, "sku": sku, "position": position, "page": 1, "total_checked": len(cards), "timestamp": datetime.now().isoformat()}
                position += 1
                if position > 100:
                    break
            await browser.close()
            return {"query": query, "sku": sku, "position": "not_found", "page": 1, "total_checked": position - 1, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            await browser.close()
            return {"error": str(e), "query": query, "sku": sku, "timestamp": datetime.now().isoformat()}

def main():
    test_cases = [
        {"query": "наушники", "sku": "1403391454"},
        {"query": "телефон", "sku": "4189905294"},
        {"query": "ноутбук", "sku": "2561680703"}
    ]
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n=== Запуск {i} ===")
        result = asyncio.run(find_ozon_position(test['query'], test['sku']))
        results.append(result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if i < len(test_cases):
            time.sleep(30)
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()