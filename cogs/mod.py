# cogs/mod.py
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

MOD_ROLE_ID = 1401053652000444517  # 👈 your mod role ID

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="delete recent messages in this channel")
    @app_commands.checks.has_role(MOD_ROLE_ID)
    @app_commands.describe(
        amount="how many messages to delete (1-1000)",
        user="only delete messages from this user",
        contains="only delete messages that contain this text",
        bots="only delete bot messages",
    )
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
        user: Optional[discord.Member] = None,
        contains: Optional[str] = None,
        bots: Optional[bool] = False,
    ):
        if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
            return await interaction.response.send_message(
                "run this in a server text channel.", ephemeral=True
            )

        perms = interaction.channel.permissions_for(interaction.guild.me)
        if not perms.manage_messages:
            return await interaction.response.send_message(
                "i need **manage messages** in this channel.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        text = (contains or "").lower()
        matched = {"n": 0}

        def check(msg: discord.Message) -> bool:
            if msg.pinned or msg.created_at < cutoff:
                return False
            if user and msg.author.id != user.id:
                return False
            if bots and not msg.author.bot:
                return False
            if text and text not in (msg.content or "").lower():
                return False
            if matched["n"] >= amount:
                return False
            matched["n"] += 1
            return True

        deleted = await interaction.channel.purge(limit=1000, check=check, bulk=True)

        filters = []
        if user: filters.append(f"user={user.display_name}")
        if contains: filters.append(f"contains='{contains}'")
        if bots: filters.append("bots-only")

        summary = (
            f"purged {len(deleted)} message(s)"
            + (f" with {'; '.join(filters)}" if filters else "")
            + ".\n"
        )

        await interaction.followup.send(summary, ephemeral=True)

    @purge.error
    async def purge_error(self, interaction: discord.Interaction, error):
        if isinstance(error, (app_commands.errors.MissingPermissions, app_commands.errors.MissingRole)):
            await interaction.response.send_message(
                "you can't do that.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
