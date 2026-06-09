import nodriver as uc
import json
import re
from datetime import datetime
import time
import asyncio

async def find_ozon_position(query: str, sku: str):
    url = f"https://www.ozon.ru/search/?text={query}&sorting=score"
    
    browser = await uc.start()
    page = await browser.get(url)
    
    print(f"Открываю: {url}")
    await asyncio.sleep(5)
    
    print("Скроллю страницу...")
    for _ in range(8):
        await page.scroll_down(800)
        await asyncio.sleep(0.8)
    
    await asyncio.sleep(2)
    
    links = await page.query_selector_all('a[href*="/product/"]')
    print(f"Найдено ссылок: {len(links)}")
    
    checked = 0
    found_position = None
    seen_skus = set()

    for link in links:
        href = link.attrs.get("href", "")
        if not href:
            continue
        
        match = re.search(r'-(\d+)/\?', href)
        if not match:
            continue
        
        found_sku = match.group(1)
        
        if found_sku in seen_skus:
            continue
        seen_skus.add(found_sku)
        
        checked += 1
        
        if found_sku == str(sku):
            found_position = checked
            break
        
        if checked >= 100:
            break
    
    return {
        "query": query,
        "sku": str(sku),
        "position": found_position if found_position else "not_found",
        "page": 1,
        "total_checked": checked,
        "timestamp": datetime.now().isoformat()
    }


def main():
    test_cases = [
        {"query": "наушники", "sku": "2770320926"},
        {"query": "телефон", "sku": "1998926953"},
        {"query": "ноутбук", "sku": "3929614690"},
    ]
    
    all_runs = []
    
    for run in range(1, 4):  
        print(f"\n{'#'*40}")
        print(f"# ПРОГОН {run}/3")
        print(f"{'#'*40}")
        
        run_results = []
        for test in test_cases:
            print(f"\n--- {test['query']} | SKU: {test['sku']}")
            result = uc.loop().run_until_complete(
                find_ozon_position(test['query'], test['sku'])
            )
            run_results.append(result)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        all_runs.append({
            "run": run,
            "results": run_results
        })
        
        if run < 3:
            time.sleep(30)
    
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(all_runs, f, indent=2, ensure_ascii=False)
    
if __name__ == "__main__":
    main()