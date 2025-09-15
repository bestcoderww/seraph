# utils/branding.py
import discord
from datetime import datetime, timezone

BRAND_COLOR = 0x6a00f4

def embed(title: str | None = None, desc: str | None = None, *, thumbnail_url: str | None = None) -> discord.Embed:
    e = discord.Embed(
        title=title or discord.Embed.Empty,
        description=desc or discord.Embed.Empty,
        color=BRAND_COLOR,
        timestamp=datetime.now(timezone.utc),  # ← aware UTC, not naive utcnow()
    )
    if thumbnail_url:
        e.set_thumbnail(url=thumbnail_url)
    e.set_footer(text="seraph")
    return e
