# cogs/info.py
import os, discord
from discord import app_commands
from discord.ext import commands
from utils.branding import embed

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._dev_ids = [int(x) for x in os.getenv("DEV_IDS", "").split(",") if x.strip()]

    def dev_mentions(self) -> str:
        return ", ".join(f"<@{i}>" for i in self._dev_ids) if self._dev_ids else "unknown"

    @app_commands.command(name="about", description="what is seraph?")
    async def about(self, interaction: discord.Interaction):
        e = embed(
            "seraph",
            "multipurpose discord bot."
        )
        e.add_field(name="developer", value=self.dev_mentions(), inline=True)
        e.add_field(name="latency", value=f"{self.bot.latency*1000:.0f} ms", inline=True)
        e.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="help", description="show commands")
    async def help(self, interaction: discord.Interaction):
        e = embed("commands", "menu")
        e.add_field(
            name="utility",
            value="`/ping`, `/profile`, `/version`",
            inline=False
        )
        e.add_field(
            name="roblox",
            value="`/rb <username>`",
            inline=False
        )
        e.add_field(
            name="bedwars",
            value="`/bw <username>`",
            inline=False
        )
        e.add_field(
            name="youtube",
            value="`/yt <search term>`",
            inline=False
        )

        e.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=e, ephemeral=True)

async def setup(bot): await bot.add_cog(Info(bot))
