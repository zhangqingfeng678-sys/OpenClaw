import discord
from discord.ext import commands
import asyncio
import websockets
import json
import os

# 從環境變數獲取 Discord Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# OpenClaw Gateway 地址，假設為本地預設地址
OPENCLAW_GATEWAY_URL = os.getenv('OPENCLAW_GATEWAY_URL', 'ws://localhost:18789')

intents = discord.Intents.default()
intents.message_content = True  # 啟用訊息內容意圖
intents.members = True # 啟用成員意圖

bot = commands.Bot(command_prefix='!', intents=intents)

async def send_to_openclaw(message_content):
    try:
        async with websockets.connect(OPENCLAW_GATEWAY_URL) as websocket:
            # 這裡需要根據 OpenClaw 的 API 格式來發送訊息
            # 假設 OpenClaw 期望一個 JSON 格式的訊息
            payload = {
                "type": "discord_message",
                "content": message_content,
                "sender": "discord_bot"
            }
            await websocket.send(json.dumps(payload))
            response = await websocket.recv()
            # 假設 OpenClaw 返回的 response 也是 JSON 格式，且包含一個 'response' 鍵
            return json.loads(response).get("response", "OpenClaw 沒有回應。")
    except Exception as e:
        print(f"連接 OpenClaw 失敗: {e}")
        return f"連接 OpenClaw 失敗: {e}"

@bot.event
async def on_ready():
    print(f'{bot.user} 已成功連接到 Discord！')
    print(f'正在嘗試連接 OpenClaw Gateway: {OPENCLAW_GATEWAY_URL}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f'收到來自 {message.author} 的訊息: {message.content}')

    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')
    elif message.content.lower() == '你好':
        await message.channel.send(f'你好 {message.author.display_name}！我是 tt 機器人。')
    else:
        # 將訊息轉發給 OpenClaw 處理
        openclaw_response = await send_to_openclaw(message.content)
        await message.channel.send(openclaw_response)

# 執行機器人
if __name__ == "__main__":
    # 從環境變數獲取 TOKEN，如果沒有則使用預設值（用於測試，實際部署應使用環境變數）
    # TOKEN = os.getenv('DISCORD_TOKEN') # 這裡已經在開頭定義了
    if not DISCORD_TOKEN:
        print("錯誤：未設定 DISCORD_TOKEN 環境變數。")
        exit(1)
    bot.run(DISCORD_TOKEN)
