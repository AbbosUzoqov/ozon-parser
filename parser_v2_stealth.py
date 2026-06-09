import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
import time

async def find_ozon_position(query, sku):
    from playwright_stealth import stealth_async  # ImportError: cannot import name 'stealth_async'
    
    url = f"https://www.ozon.ru/search/?text={query}&sorting=score"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='ru-RU',
        )
        page = await context.new_page()
        await stealth_async(page)  # не работает - неправильное имя функции
        
        await page.goto(url, timeout=60000, wait_until='domcontentloaded')
        await page.wait_for_timeout(4000)
        
        for _ in range(8):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(600)
        
        links = await page.query_selector_all('a[href*="/product/"]')
        
        checked = 0
        for link in links:
            href = await link.get_attribute('href')
            if not href:
                continue
            import re
            match = re.search(r'-i-(\d+)/', href)
            if not match:
                continue
            checked += 1
            if match.group(1) == str(sku):
                await browser.close()
                return {"query": query, "sku": sku, "position": checked, "page": 1, "total_checked": checked, "timestamp": datetime.now().isoformat()}
            if checked >= 100:
                break
        
        await browser.close()
        return {"query": query, "sku": sku, "position": "not_found", "page": 1, "total_checked": checked, "timestamp": datetime.now().isoformat()}

def main():
    test_cases = [
        {"query": "наушники", "sku": "1403391454"},
        {"query": "телефон", "sku": "4189905294"},
        {"query": "ноутбук", "sku": "2561680703"}
    ]
    for i, test in enumerate(test_cases, 1):
        result = asyncio.run(find_ozon_position(test['query'], test['sku']))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if i < len(test_cases):
            time.sleep(30)

if __name__ == "__main__":
    main()