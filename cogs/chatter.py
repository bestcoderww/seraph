# cogs/chatter.py
import re, random, time
import discord
from discord.ext import commands

# optional: restrict to specific channels (fill with channel IDs or leave empty)
ALLOWED_CHANNEL_IDS: set[int] = set()  # e.g., {123456789012345678}

# simple cooldown per channel to prevent spam (seconds)
CHANNEL_COOLDOWN = 3.0

# basic keyword → responses (add your own!)
TRIGGERS = [
    (re.compile(r"\b(hi|hello|hey|yo|sup)\b", re.I), [
        "hey", "hi", "how are you?", "what's up?"
    ]),
    (re.compile(r"\b(bye|gn|goodnight|good night|cya|see ya|pce)\b", re.I), [
        "later", "good night", "bye", "o/"
    ]),
]

MENTION_REPLIES = [
    "hello!️", "sup?",
    "bedwars?", "sybau"
]

class Chatter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_reply_ts: dict[int, float] = {}  # channel_id -> last time we replied

    def _cooldown_ok(self, channel_id: int) -> bool:
        now = time.time()
        last = self._last_reply_ts.get(channel_id, 0.0)
        if now - last >= CHANNEL_COOLDOWN:
            self._last_reply_ts[channel_id] = now
            return True
        return False

    def _allowed_channel(self, channel: discord.abc.Messageable) -> bool:
        if not ALLOWED_CHANNEL_IDS:
            return True
        return getattr(channel, "id", None) in ALLOWED_CHANNEL_IDS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # ignore ourselves & other bots
        if message.author.bot:
            return
        if not message.guild:
            return  # skip DMs (change if you want DM support)
        if not self._allowed_channel(message.channel):
            return

        # allow slash/legacy commands to still work
        # (not strictly needed for slash, but good practice)
        # await self.bot.process_commands(message)  # only if you use prefix commands

        # basic per-channel cooldown
        if not self._cooldown_ok(message.channel.id):
            return

        content = message.content.strip()

        # 1) reply to mentions
        if self.bot.user and (self.bot.user in message.mentions):
            await message.reply(random.choice(MENTION_REPLIES))
            return

        # 2) keyword triggers
        for pattern, replies in TRIGGERS:
            if pattern.search(content):
                await message.reply(random.choice(replies))
                return

async def setup(bot: commands.Bot):
    await bot.add_cog(Chatter(bot))
