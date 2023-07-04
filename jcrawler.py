import json
import pandas as pd
import os
import asyncio
from pionex.trade import start_trading
from telegram.get_message import start_telegram

def load_config():
    with open('./pionex/config.json', 'r') as f:
        config = json.load(f)
        return config['key'], config['secret'], config['order_amount']

async def create_config():
    # 若pionex/config.json不存在就建立
    if not os.path.isfile('./pionex/config.json'):
        # 建立config.json
        config = {
            "key": "",
            "secret": ""
        }
        with open('./pionex/config.json', 'w') as f:
            json.dump(config, f, indent=4)
    
    # 若telegram/config.json不存在就建立
    if not os.path.isfile('./telegram/config.json'):
        # 建立config.json
        config = {
            "api_id": "",
            "api_hash": ""
        }
        with open('./telegram/config.json', 'w') as f:
            json.dump(config, f, indent=4)

async def create_csv():
    # 建立用來儲存下單記錄的csv，主要是供Sell時能知道當初買了多少幣
    if not os.path.isfile('./record.csv'):
        df = pd.DataFrame(columns=["orderId", "symbol", "price", "size", "fee", "date", "strategy"])
        df.to_csv('./record.csv', index=False)

async def main():
    queue = asyncio.Queue()

    API_KEY, API_SECRET, order_amount = load_config()

    # Start the Telegram client
    telegram_task = asyncio.create_task(start_telegram(queue))

    # Start the trading bot
    trading_task = asyncio.create_task(start_trading(queue, API_KEY, API_SECRET, order_amount))

    # Wait for both tasks to complete
    await asyncio.gather(telegram_task, trading_task)

if __name__ == "__main__":
    asyncio.run(create_config())
    asyncio.run(create_csv())
    asyncio.run(main())
