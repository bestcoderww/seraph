# cogs/util.py
import discord
from discord.ext import commands
from discord import app_commands
import os

UTIL_ROLE_ID = 1400604190203449414  # 🔒 only this role can use /stop
BOT_ENV = os.getenv("BOT_ENV", "unknown").lower()

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="version", description="displays which version of bot is active")
    async def version(self, interaction: discord.Interaction):
        env = BOT_ENV.capitalize() if BOT_ENV != "unknown" else "a mystery"
        await interaction.response.send_message(f"running from: **{env}**", ephemeral=True)

    @app_commands.command(name="stop", description="shut the bot down")
    @app_commands.checks.has_role(UTIL_ROLE_ID)
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.send_message("shutting down the bot...", ephemeral=True)
        await self.bot.close()

    @stop.error
    async def stop_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingRole):
            await interaction.response.send_message(
                "you can't do that.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))
