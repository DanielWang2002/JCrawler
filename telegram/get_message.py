import asyncio
import json
import time
from telethon.sync import TelegramClient, events
from .tg_utils import biao_bi
from utils.jc_utils import logger

def load_config():
    with open('./telegram/config.json', 'r') as f:
        config = json.load(f)
        return config['app_id'], config['app_hash'], config['channel']

api_id, api_hash, channel_username = load_config()

async def start_telegram(queue):
    try:
        # 建立TelegramClient物件
        client = TelegramClient('anon', api_id, api_hash)

        # 定義事件處理器
        @client.on(events.NewMessage(chats=channel_username))
        async def handle_new_message(event):
            message = event.message
            logger(f"收到來自Telegram的訊息\n\n{message.text}")
            if message.text:
                msg = message.text.split("\n")
                if msg[0] == "【飆幣系統 進場】" or msg[0] == "【飆幣系統 出場】":
                    signal = biao_bi(message)
                    # print(signal)
                    await queue.put(signal)

        # 啟動TelegramClient
        async with client:
            # 開始監聽事件
            logger("JCrawler Telegram Start")
            await client.run_until_disconnected()

    except Exception as e:
        # 重新啟動start_telegram
        logger(f"JCrawler Telegram Error: {e}")
        await asyncio.sleep(5)
        await start_telegram(queue)
