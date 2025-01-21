import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
import json
import sqlite3
from discord import ButtonStyle
import discord.ui
# from discord.ui import Button, ButtonStyle
import asyncio

# Get configuration.json
with open("configuration.json", "r") as config:
    data = json.load(config)
    token = data["token"]
    prefix = data["prefix"]

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(prefix, intents = intents)

class help(commands.Cog, name="help", description="Learn about the commands you can use in this server"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="help", description="Learn about the commands you can use in this server")
    async def help(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
        title=f"What commands can I use in this server? <a:cutestar:1236936244722925609>",
        description="Here's a list!",
        color = discord.Color(0x2B2D31)
        )
        embed.add_field(name="/serverinfo", value="Shows you some cool information about the server", inline=False)
        embed.add_field(name="/status focus", value="This sets your status to **focus** and hides non-study related channels.", inline=False)
        embed.add_field(name="/status unfocus", value="This removes your **focus** status and unhides non-study related channels.", inline=False)
        embed.add_field(name="/fun wordle", value="Gives you the link of today's Wordle.", inline=False)
        embed.add_field(name="/fun coinflip", value="Flips a coin for you.", inline=False)
        embed.add_field(name="/fun rolldice", value="Rolls a 6-sided dice for you.", inline=False)
        embed.add_field(name="/fun dadjoke", value="Gives you a corny dad joke.", inline=False)
        embed.add_field(name="/fun clapback", value="Places :clap: between your words and claps right back at you.", inline=False)
        embed.add_field(name="/colors pastel", value="Pick a pastel color role.", inline=False)
        embed.add_field(name="/colors chromatic", value="Pick a chromatic color role.", inline=False)
        embed.add_field(name="/room create", value="Create a private voice channel.", inline=False)
        embed.add_field(name="/room request", value="Request to join a private voice channel.", inline=False)
        embed.add_field(name="/rank profile", value="View your study statistics.", inline=False)
        embed.add_field(name="/rank daily", value="View your daily study statistics.", inline=False)
        embed.add_field(name="/rank monthly", value="View your monthly study statistics.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(help(bot))