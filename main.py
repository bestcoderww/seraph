import os, sys, logging
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1400529660357644430
GUILD = discord.Object(id=GUILD_ID)


PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
print(f"[path] project root on sys.path: {PROJECT_ROOT}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="ping", description="check if the bot is alive")
@app_commands.guilds(GUILD)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong 🏓", ephemeral=False)
async def setup_hook():
    from pathlib import Path
    DEBUG = os.getenv("DEBUG", "False") == "True"

    cogs_dir = Path(__file__).parent / "cogs"
    for py in cogs_dir.glob("*.py"):
        if py.stem.startswith("_"):
            continue
        await bot.load_extension(f"cogs.{py.stem}")

    if DEBUG:
        # copy global commands into guild for instant testing (no re-ghosting)
        bot.tree.copy_global_to(guild=GUILD)
        synced = await bot.tree.sync(guild=GUILD)
        print(f"✅ synced {len(synced)} guild commands to {GUILD_ID}")
        print("🛠️ running in DEBUG mode — only syncing to dev server")
    else:
        # global sync only if you deploy again (just for future prod use)
        synced = await bot.tree.sync()
        print(f"🌐 synced {len(synced)} global commands")
        print("🚀 running in PRODUCTION mode — syncing globally")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="the sky")
    )
    print(f"logged in as {bot.user} (id: {bot.user.id})")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not TOKEN:
        raise RuntimeError("set DISCORD_TOKEN in your .env")
    bot.run(TOKEN)
