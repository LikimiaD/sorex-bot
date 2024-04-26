import asyncio

import aiohttp
import requests
from datetime import datetime
from asyncio.queues import Queue

from database.queries.core import AsyncORM


class CryptoMonitor:
    API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    def __init__(self, api_key, bot, max_workers):
        self.api_key = api_key
        self.bot = bot
        self.max_workers = max_workers
        self.queue = Queue()

    async def fetch_currency_prices(self, currencies):
        headers = {
            'Accept': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        params = {
            'symbol': ','.join(currencies)
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {currency: data['data'][currency]['quote']['USD']['price'] for currency in currencies}
                else:
                    return None

    async def worker(self, name):
        while True:
            alert = await self.queue.get()
            if not isinstance(alert, dict):
                print(f"Error: Expected dict, got {type(alert)} with value {alert}")
                continue

            try:
                prices = await self.fetch_currency_prices([alert['cryptocurrency']])
                price = prices.get(alert['cryptocurrency'])
                if price:
                    if (alert['direction'] == "above" and price >= alert['threshold_value']) or (
                            alert['direction'] == "below" and price <= alert['threshold_value']):
                        message_text = f"{datetime.now()}\n{alert['cryptocurrency']}\nYour alert for {alert['cryptocurrency']} has triggered at ${price:.2f}"
                        await self.bot.send_message(alert['telegram_id'], message_text)
            except Exception as e:
                print(f"Error in worker {name}: {e}")
            finally:
                self.queue.task_done()

    async def run_workers(self):
        while True:
            workers = [asyncio.create_task(self.worker(f"Worker-{i}")) for i in range(self.max_workers)]
            alerts = await AsyncORM.get_alerts()
            for alert in alerts:
                await self.queue.put(alert)
            await self.queue.join()
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers, return_exceptions=True)
            await asyncio.sleep(240)


async def monitor(api_key, bot, max_workers):
    crypto_monitor = CryptoMonitor(api_key, bot, max_workers)
    await crypto_monitor.run_workers()
