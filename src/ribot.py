import os
import discord
from discord.ext import tasks

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    hello_loop.start()

@tasks.loop(minutes=1)
async def hello_loop():
    # テスト用：全サーバーの最初のテキストチャンネルに送信
    for guild in client.guilds:
        for channel in guild.text_channels:
            try:
                await channel.send("Hello")
                break
            except Exception:
                continue

client.run(DISCORD_BOT_TOKEN)
