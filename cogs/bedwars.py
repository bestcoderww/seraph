# cogs/bedwars.py
import os, aiohttp, discord
from discord.ext import commands
from discord import app_commands

HYPIXEL_KEY = os.getenv("HYPIXEL_KEY")

API_MOJANG = "https://api.mojang.com/users/profiles/minecraft/{username}"
API_HYPIXEL_V2 = "https://api.hypixel.net/v2/player?uuid={uuid}"
API_HYPIXEL_V1 = "https://api.hypixel.net/player?key={key}&uuid={uuid}"

TIMEOUT = aiohttp.ClientTimeout(total=12)

async def _get_json(session, url, headers=None):
    async with session.get(url, headers=headers or {}) as r:
        if r.status == 204:  # Mojang returns 204 when name not found
            return r.status, None
        data = await r.json(content_type=None)
        return r.status, data

def _safe_int(d, k, default=0):
    try:
        return int(d.get(k, default) or 0)
    except Exception:
        return default

def _ratio(a, b):
    return float(a) if b == 0 else a / b

class BedWars(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bw", description="hypixel bedwars stats")
    @app_commands.describe(username="minecraft username")
    async def bw(self, interaction: discord.Interaction, username: str):
        await interaction.response.defer(thinking=True)

        if not HYPIXEL_KEY:
            return await interaction.followup.send(
                "hypixel_key is not set.",
                ephemeral=True
            )

        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            # 1) Mojang: username -> UUID
            st, mojang = await _get_json(session, API_MOJANG.format(username=username))
            if not mojang or "id" not in (mojang or {}):
                return await interaction.followup.send(f"player `{username}` not found.", ephemeral=True)
            uuid = mojang["id"]
            ign = mojang.get("name", username)

            # 2) Hypixel v2 (header), fallback to v1 (?key=)
            player = None
            st2, data2 = await _get_json(session, API_HYPIXEL_V2.format(uuid=uuid),
                                         headers={"API-Key": HYPIXEL_KEY})
            if data2 and data2.get("success"):
                player = data2.get("player")
            if player is None:
                st1, data1 = await _get_json(session, API_HYPIXEL_V1.format(key=HYPIXEL_KEY, uuid=uuid))
                if data1 and data1.get("success"):
                    player = data1.get("player")

        if not player:
            return await interaction.followup.send("player has no hypixel profile or api error.", ephemeral=True)

        stats_root = player.get("stats", {}) or {}
        bw = stats_root.get("Bedwars") or stats_root.get("BedWars") or {}
        if not bw:
            return await interaction.followup.send("no bedwars stats found).", ephemeral=True)

        # gather numbers
        level = int(player.get("achievements", {}).get("bedwars_level", 0))
        wins = _safe_int(bw, "wins_bedwars")
        losses = _safe_int(bw, "losses_bedwars")
        fkills = _safe_int(bw, "final_kills_bedwars")
        fdeaths = _safe_int(bw, "final_deaths_bedwars")
        beds_broken = _safe_int(bw, "beds_broken_bedwars")
        beds_lost = _safe_int(bw, "beds_lost_bedwars")

        wlr = _ratio(wins, losses)
        fkdr = _ratio(fkills, fdeaths)
        bblr = _ratio(beds_broken, beds_lost)

        # build EXACT format (plain text). remove .lower() if you want original casing.
        header = f"**bw** - displaying stats for `[✫{level}] {ign.lower()}`"
        lines = [
            header,
            f"wlr: `{wlr:.2f}` (wins: `{wins}` | losses: `{losses}`)",
            f"fkdr: `{fkdr:.2f}` (final kills: `{fkills}` | final deaths: `{fdeaths}`)",
            f"bblr: `{bblr:.2f}` (beds broken: `{beds_broken}` | beds lost: `{beds_lost}`)",
        ]

        await interaction.followup.send("\n".join(lines))

async def setup(bot: commands.Bot):
    await bot.add_cog(BedWars(bot))
