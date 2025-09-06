# cogs/roblox.py
import aiohttp, discord
from discord.ext import commands
from discord import app_commands

API_USERNAMES = "https://users.roblox.com/v1/usernames/users"  # POST
API_USER_INFO = "https://users.roblox.com/v1/users/{user_id}"
API_HEADSHOT  = "https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=false"
API_COLLECT   = "https://economy.roblox.com/v1/users/{user_id}/assets/collectibles?limit=100&sortOrder=Asc{cursor}"

TIMEOUT = aiohttp.ClientTimeout(total=12)

class Roblox(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def username_to_id(self, session: aiohttp.ClientSession, username: str) -> tuple[int | None, str | None]:
        # docs: POST { usernames: [..], excludeBannedUsers: true }
        payload = {"usernames": [username], "excludeBannedUsers": True}
        async with session.post(API_USERNAMES, json=payload) as r:
            if r.status != 200:
                return None, None
            data = await r.json()
        users = data.get("data") or []
        if not users:
            return None, None
        u = users[0]
        return u.get("id"), u.get("requestedUsername") or username

    @app_commands.command(name="rb", description="look up a roblox user")
    @app_commands.describe(username="roblox username")
    async def roblox(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)

        async with aiohttp.ClientSession(timeout=TIMEOUT, headers={"User-Agent": "wingman/1.0"}) as session:
            # 1) username -> id (new endpoint)
            uid, uname = await self.username_to_id(session, username)
            if not uid:
                return await interaction.followup.send(f"user `{username}` not found.", ephemeral=True)
            # 2) profile info
            async with session.get(API_USER_INFO.format(user_id=uid)) as r:
                if r.status != 200:
                    return await interaction.followup.send("failed to fetch user profile.", ephemeral=True)
                info = await r.json()

            display_name = info.get("displayName") or uname
            created = info.get("created", "unknown")
            description = (info.get("description") or "").strip()

            # 3) headshot
            async with session.get(API_HEADSHOT.format(user_id=uid)) as r:
                head_json = await r.json()
            head_url = None
            if head_json.get("data"):
                head_url = head_json["data"][0].get("imageUrl")

            # 4) RAP (paginate collectibles)
            total_rap = 0
            item_count = 0
            cursor = ""
            try:
                # cap pages to avoid abuse (3*100 = 300 items should be enough for most)
                pages = 0
                while pages < 10:  # raise if you want to allow more pages
                    url = API_COLLECT.format(user_id=uid, cursor=f"&cursor={cursor}" if cursor else "")
                    async with session.get(url) as r:
                        if r.status != 200:
                            break
                        data = await r.json()
                    for it in data.get("data", []):
                        rap = it.get("recentAveragePrice")
                        if isinstance(rap, (int, float)):
                            total_rap += int(rap)
                        item_count += 1
                    cursor = data.get("nextPageCursor")
                    pages += 1
                    if not cursor:
                        break
            except Exception:
                pass  # keep whatever we accumulated

        # 5) plain text output (no embeds)
        lines = [
            f"roblox user: {uname} ({display_name})",
            f"user id: {uid}",
            f"created: {created}",
            f"rap: {total_rap} (items: {item_count})",
            f"profile: https://www.roblox.com/users/{uid}/profile",
        ]
        if head_url:
            lines.append(f"headshot: {head_url}")
        if description:
            lines.append(f"description: {description[:247] + '...' if len(description) > 250 else description}")

        await interaction.followup.send("\n".join(lines))

async def setup(bot: commands.Bot):
    await bot.add_cog(Roblox(bot))
