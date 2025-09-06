import os, sys, logging, asyncio, platform
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path

# --- env / paths ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DEBUG = os.getenv("DEBUG", "False") == "True"

GUILD_ID = 1400529660357644430
GUILD = discord.Object(id=GUILD_ID)

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
print(f"[path] project root on sys.path: {PROJECT_ROOT}")

# --- discord bot setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="ping", description="check if the bot is alive")
@app_commands.guilds(GUILD)
async def ping(interaction: discord.Interaction):
    # fast response keeps interactions happy
    await interaction.response.send_message("pong 🏓", ephemeral=False)

async def setup_hook():
    # load all cogs in /cogs (skip files starting with _)
    cogs_dir = Path(__file__).parent / "cogs"
    for py in cogs_dir.glob("*.py"):
        if py.stem.startswith("_"):
            continue
        await bot.load_extension(f"cogs.{py.stem}")

    # sync commands (guild for fast dev; global for prod)
    if DEBUG:
        bot.tree.copy_global_to(guild=GUILD)
        synced = await bot.tree.sync(guild=GUILD)
        print(f"✅ synced {len(synced)} guild commands to {GUILD_ID}")
        print("🛠️ DEBUG mode — syncing only to dev server")
    else:
        synced = await bot.tree.sync()
        print(f"🌐 synced {len(synced)} global commands")
        print("🚀 PRODUCTION mode — syncing globally")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    host = platform.node()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"the sky · {host}")
    )
    print(f"[ready] logged in as {bot.user} (id: {bot.user.id}) on {host}")

# --- tiny aiohttp web server for Render Web Service ---
from aiohttp import web

async def handle_root(_request):
    return web.Response(text="wingman bot: alive")

async def run_webserver():
    port = int(os.environ.get("PORT", "8080"))  # Render provides $PORT
    app = web.Application()
    app.router.add_get("/", handle_root)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[web] running on 0.0.0.0:{port}")

# --- run bot + web together ---
async def main():
    if not TOKEN:
        raise RuntimeError("set DISCORD_TOKEN in environment (Render → Environment → Add Variable)")

    # run both concurrently: the bot and the web server
    await asyncio.gather(
        bot.start(TOKEN),
        run_webserver(),
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
