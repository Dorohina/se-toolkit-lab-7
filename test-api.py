import httpx
import asyncio
from datetime import datetime

async def test():
    all_logs = []
    async with httpx.AsyncClient(timeout=60) as client:
        try:
            cursor = None
            page_num = 0
            while True:
                page_num += 1
                params = {"limit": 500}
                if cursor:
                    params["since"] = cursor
                
                print(f"Fetching page {page_num}...")
                resp = await client.get(
                    "https://auche.namaz.live/api/logs",
                    params=params,
                    auth=("v.dorokhina@innopolis.university", "Dorohinaekacucumber6")
                )
                print(f"Page {page_num} Status: {resp.status_code}")
                data = resp.json()
                logs = data.get('logs', [])
                all_logs.extend(logs)
                print(f"Got {len(logs)} logs, total: {len(all_logs)}")
                
                if not data.get('has_more') or not logs:
                    break
                
                cursor = logs[-1]['submitted_at']
                print(f"Next cursor: {cursor}")
            
            print(f"\nTotal logs fetched: {len(all_logs)}")
        except Exception as e:
            print(f"Error on page {page_num}: {type(e).__name__}: {e}")

asyncio.run(test())
