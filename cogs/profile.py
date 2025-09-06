# cogs/profile.py
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="profile",
        description="get a user's avatar and banner (by mention or id)"
    )
    @app_commands.describe(
        user="pick a user (mention)",
        user_id="or paste a discord id (numbers only)",
        size="image size (128-4096, powers of two work best)",
        server_avatar="prefer the server-specific avatar when possible"
    )
    async def profile(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.User] = None,
        user_id: Optional[str] = None,
        size: app_commands.Range[int, 128, 4096] = 1024,
        server_avatar: Optional[bool] = True,
    ):
        # Public reply (so your friend can see too)
        await interaction.response.defer(thinking=True)

        # 1) resolve target
        target: Optional[discord.abc.User] = user
        if target is None and user_id:
            try:
                uid = int(user_id.strip())
            except ValueError:
                return await interaction.followup.send("that doesn't look like a valid id.", ephemeral=True)
            try:
                target = await self.bot.fetch_user(uid)  # works globally
            except discord.NotFound:
                return await interaction.followup.send("no user found for that id.", ephemeral=True)
            except discord.HTTPException:
                return await interaction.followup.send("failed to fetch that user (rate limit or network).", ephemeral=True)

        if target is None:
            target = interaction.user  # default to the invoker

        # 2) compute avatar URL
        avatar_url: str
        member = None
        if interaction.guild:
            member = interaction.guild.get_member(target.id)

        # prefer server-specific avatar if requested and we have a Member
        if server_avatar and isinstance(member, discord.Member):
            avatar_url = member.display_avatar.replace(size=size).url
        else:
            avatar_url = target.display_avatar.replace(size=size).url

        # 3) fetch full user to get banner (must use fetch_user)
        try:
            full_user = await self.bot.fetch_user(target.id)
        except discord.HTTPException:
            full_user = None

        banner_url = None
        if full_user and full_user.banner:
            # .banner is an Asset
            banner_url = full_user.banner.with_size(size).url

        # 4) plain-text output
        who = getattr(target, "display_name", str(target))
        lines = [
            f"profile for {who} ({target.id})",
            f"avatar ({size}px): {avatar_url}",
            f"banner ({size}px): {banner_url if banner_url else 'no banner set'}",
        ]
        await interaction.followup.send("\n".join(lines))

async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
