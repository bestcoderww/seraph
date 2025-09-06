# cogs/fun.py
import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="play rock-paper-scissors")
    @app_commands.describe(choice="choose: rock, paper, or scissors")
    async def rps(self, interaction: discord.Interaction, choice: str):
        player_choice = choice.lower()
        options = ["rock", "paper", "scissors"]
        if player_choice not in options:
            return await interaction.response.send_message("choose rock, paper, or scissors.", ephemeral=True)

        bot_choice = random.choice(options)

        # determine outcome
        if player_choice == bot_choice:
            result = "it's a tie!"
        elif (
            (player_choice == "rock" and bot_choice == "scissors") or
            (player_choice == "paper" and bot_choice == "rock") or
            (player_choice == "scissors" and bot_choice == "paper")
        ):
            result = "you win 🎉"
        else:
            result = "you lose 😢"

        await interaction.response.send_message(
            f"you chose **{player_choice}**.\n"
            f"i chose **{bot_choice}**.\n\n**{result}**"
        )

async def setup(bot): await bot.add_cog(Fun(bot))
