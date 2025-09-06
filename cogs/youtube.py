# cogs/youtube.py
import discord, re, urllib.parse, aiohttp
from discord.ext import commands
from discord import app_commands

# preferred: library search (robust)
try:
    from youtubesearchpython import VideosSearch
    HAVE_LIB = True
except Exception:
    HAVE_LIB = False

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="yt", description="search youtube and return the first video")
    @app_commands.describe(query="what to search for")
    async def yt(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=False, thinking=True)

        # 1) use the library if installed
        if HAVE_LIB:
            try:
                vs = VideosSearch(query, limit=1)
                data = vs.result()  # sync method is fine here; it's quick
                items = data.get("result") or []
                if items:
                    vid = items[0]
                    link = vid.get("link")
                    title = vid.get("title") or "youtube"
                    thumb = (vid.get("thumbnails") or [{}])[-1].get("url")
                    duration = vid.get("duration") or ""
                    embed = discord.Embed(title=title, url=link, description=duration)
                    if thumb:
                        embed.set_thumbnail(url=thumb)
                    return await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception:
                pass  # fall back below

        # 2) fallback: parse the mobile site (lighter markup)
        try:
            search_url = "https://m.youtube.com/results?search_query=" + urllib.parse.quote(query)
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                    html = await resp.text()

            m = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', html)
            if not m:
                return await interaction.followup.send("no results found.", ephemeral=True)

            video_id = m.group(1)
            link = f"https://www.youtube.com/watch?v={video_id}"
            await interaction.followup.send(f"🎬 {link}", ephemeral=True)
        except Exception:
            await interaction.followup.send("failed to search youtube.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(YouTube(bot))
