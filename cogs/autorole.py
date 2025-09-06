# cogs/autorole.py
import discord
import json
from discord.ext import commands
from discord import app_commands
from pathlib import Path

MOD_ROLE_ID = 1401053652000444517
DATA_FILE = Path("data/autorole.json")

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autorole_data = self.load_data()

    def load_data(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_data(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self.autorole_data, f, indent=2)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = str(member.guild.id)
        role_id = self.autorole_data.get(guild_id)

        if role_id:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role)
                    print(f"✅ gave {member.name} the '{role.name}' role")
                except discord.Forbidden:
                    print("❌ missing permissions to add role")
            else:
                print("❌ role not found")



    @app_commands.command(name="setautorole", description="set the default role given to new members")
    @app_commands.checks.has_role(MOD_ROLE_ID)
    @app_commands.describe(role="the role to automatically assign on join")
    async def setautorole(self, interaction: discord.Interaction, role: discord.Role):
        self.autorole_data[str(interaction.guild.id)] = role.id
        self.save_data()
        await interaction.response.send_message(
            f"✅ new members will now get the **{role.name}** role.", ephemeral=True
        )

    @setautorole.error
    async def setautorole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingRole):
            await interaction.response.send_message(
                "🚫 you don’t have permission to use this command.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRole(bot))
