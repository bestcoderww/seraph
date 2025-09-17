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

# keep your dev guild id if you want to do fast, *temporary* guild syncs during debugging
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

# GLOBAL command (no guild decorator)
@bot.tree.command(name="ping", description="check if the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong 🏓", ephemeral=False)

async def setup_hook():
    # load all cogs in /cogs (skip files starting with _)
    cogs_dir = Path(__file__).parent / "cogs"
    for py in cogs_dir.glob("*.py"):
        if py.stem.startswith("_"):
            continue
        await bot.load_extension(f"cogs.{py.stem}")

    # sync once only, to avoid double registration during rolling restarts
    if getattr(bot, "_synced_once", False):
        return

    # --- broom pass ---
    # if you previously had guild-scoped commands, this clears them from the dev guild
    # so only the global copies remain (prevents duplicates in that guild).
    try:
        bot.tree.clear_commands(guild=GUILD)
        await bot.tree.sync(guild=GUILD)  # push the empty set to delete old guild cmds
        print(f"🧹 cleared any old guild commands in {GUILD_ID}")
    except Exception as e:
        print(f"⚠️ guild clear/sync skipped or failed: {e}")

    # --- GLOBAL SYNC ONLY ---
    synced = await bot.tree.sync()
    print(f"🌐 synced {len(synced)} global commands")

    bot._synced_once = True  # guard flag

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    host = platform.node()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="the sky"),
    )
    print(f"[ready] logged in as {bot.user} (id: {bot.user.id}) on {host}")

# --- tiny aiohttp web server for Render Web Service ---
from aiohttp import web

async def handle_root(_request):
    return web.Response(text="seraph: alive")

async def handle_healthz(_request):
    return web.Response(text="ok")

async def run_webserver():
    port = int(os.environ.get("PORT", "8080"))  # Render provides $PORT
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/healthz", handle_healthz)  # optional health endpoint
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
