# cogs/infos.py
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class InfoExtra(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="get info about a user")
    @app_commands.describe(user="user to get info about (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"{user} ({user.id})",
            description=f"info about {user.mention}",
            color=discord.Color.blurple(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)
        embed.add_field(name="joined", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC") if user.joined_at else "unknown", inline=True)
        embed.add_field(name="roles", value=", ".join(r.mention for r in user.roles[1:]) or "none", inline=False)
        embed.set_footer(text=f"requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="get info about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"{guild.name} ({guild.id})",
            description="info about this server",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=True)
        embed.add_field(name="members", value=guild.member_count, inline=True)
        embed.add_field(name="roles", value=len(guild.roles), inline=True)
        embed.add_field(name="channels", value=len(guild.channels), inline=True)
        embed.set_footer(text=f"requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot): await bot.add_cog(InfoExtra(bot))
