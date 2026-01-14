import os
import datetime
import dotenv
import discord

from discord.ext import commands, tasks
from database import SqliteDatabase

#------------------------------------------------------------------------------
# 環境変数
#------------------------------------------------------------------------------
dotenv.load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

#------------------------------------------------------------------------------
# Discord Bot 初期化
#------------------------------------------------------------------------------
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#------------------------------------------------------------------------------
# DB 初期化
#------------------------------------------------------------------------------
db = SqliteDatabase("/app/data/RiBot.db")

db.execute("""
CREATE TABLE IF NOT EXISTS server_table (
    server_id INTEGER PRIMARY KEY,
    notify_channel_id INTEGER
)
""")

#------------------------------------------------------------------------------
# スラッシュコマンド
#------------------------------------------------------------------------------
@bot.tree.command(name="register_notify_channel", description="通知用チャンネルの登録")
async def register_notify_channel(interaction:discord.Interaction, channel:discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return
    
    server_id = interaction.guild_id
    channel_id = channel.id
    db.execute("INSERT INTO server_table (server_id, notify_channel_id) VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET notify_channel_id = excluded.notify_channel_id",
        (server_id, channel_id))
    
    await interaction.response.send_message(f"通知チャンネルを {channel.mention} に登録しました。", ephemeral=True)

@bot.tree.command(name="unregister_notify_channel", description="通知用チャンネルの解除")
async def unregister_notify_channel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("このコマンドは管理者のみ使用できます。", ephemeral=True)
        return
    
    server_id = interaction.guild_id
    db.execute("UPDATE server_table SET notify_channel_id = NULL WHERE server_id = ?",
        (server_id,))

    await interaction.response.send_message("通知チャンネルの登録を解除しました。", ephemeral=True)

#------------------------------------------------------------------------------
# イベント
#------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # 起動時にサーバーIDを保存
    for guild in bot.guilds:
        db.execute(
            "INSERT OR IGNORE INTO server_table (server_id) VALUES (?)",
            (guild.id,)
        )
    if not send_hello.is_running():
        send_hello.start()

    await bot.tree.sync()

@bot.event
async def on_guild_join(guild: discord.Guild):
    db.execute(
        "INSERT OR IGNORE INTO server_table (server_id) VALUES (?)",
        (guild.id,)
    )

@bot.event
async def on_guild_remove(guild: discord.Guild):
    db.execute(
        "DELETE FROM server_table WHERE server_id = ?",
        (guild.id,)
    )

#------------------------------------------------------------------------------
# 定期実行
#------------------------------------------------------------------------------
#JST = datetime.timezone(datetime.timedelta(hours=9))
#time=datetime.time(hour=9, minute=0, tzinfo=JST)
@tasks.loop(minutes=1)
async def send_hello():
    rows = db.fetchall("SELECT notify_channel_id FROM server_table WHERE notify_channel_id IS NOT NULL")
    for row in rows:
        channel = bot.get_channel(row[0])
        if(channel):
            await channel.send("Hello")

@send_hello.before_loop
async def before_send_hello():
    await bot.wait_until_ready()

#------------------------------------------------------------------------------
# 起動
#------------------------------------------------------------------------------
bot.run(DISCORD_BOT_TOKEN)
