import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
import json
import random
import sqlite3
from discord import ButtonStyle
import discord.ui
import asyncio
# import urbandict

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

class fun(commands.GroupCog, name="fun", description="Entertainment commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
    @app_commands.command(name="wordle", description="Get today's Wordle link")
    async def wordle(self, interaction: discord.Interaction) -> None:
        wordle_link = "https://www.nytimes.com/games/wordle/index.html"
        embed = discord.Embed(
            title="Today's Wordle",
            description=f"<a:wordlesolve:1241879849979613244> [Click here to play Wordle]({wordle_link})",
            color=discord.Color.from_rgb(96, 157, 86)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    async def coinflip(self, interaction: discord.Interaction) -> None:
        outcome = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="Coin Flip",
            description=f"<a:goldcoin:1241879567187054602> The coin landed on: **{outcome}**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rolldice", description="Roll a 6-sided dice")
    async def rolldice(self, interaction: discord.Interaction) -> None:
        roll = random.randint(1, 6)
        embed = discord.Embed(
            title="Dice Roll",
            description=f"<a:diceroll:1241879749194940469> You rolled a: **{roll}**",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pick", description="Picks a random choice, use commas for multi-word options")
    async def pick(self, interaction: discord.Interaction, options: str) -> None:
        out = random.choice(options.split(","))
        embed = discord.Embed(
            title="Random Choice",
            description=f"**SERENA picked:** {out}",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="eightball", description="Ask 8-ball for your destiny")
    async def eightball(self, interaction: discord.Interaction, question: str) -> None:
        eight_ball_responses = [
                "It is certain",
                "It is decidedly so",
                "Without a doubt",
                "Yes, definitely",
                "You may rely on it",
                "As I see it, yes",
                "Most likely",
                "Outlook good",
                "Yes",
                "Signs point to yes",
                "Reply hazy try again",
                "Ask again later",
                "Better not tell you now",
                "Cannot predict now",
                "Concentrate and ask again",
                "Don't count on it",
                "My reply is no",
                "My sources say no",
                "Outlook not so good",
                "Very doubtful"
            ]
        eightballans = random.choice(eight_ball_responses)
        embed = discord.Embed(
            title="8-ball says:",
            description=f":8ball: **{eightballans}**",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="Your Question: ", value=question, inline=False)
        await interaction.response.send_message(embed=embed)    

    # @app_commands.command(name="urbandictionary", description="Gives you the definition of a word from the much trusted Urban Dictionary")
    # async def urbandictionary(self, interaction: discord.Interaction, word: str) -> None:
        
    #     out = 
    #     embed = discord.Embed(
    #         title=f"Definition of {word}",
    #         description=f"**Urban Dictionary says:",
    #         color=discord.Color.dark_blue()
    #     )
    #     await interaction.response.send_message(embed=embed)
     
    @app_commands.command(name = "dadjoke", description = "Get a random dad joke")
    async def dadjoke(self, interaction: discord.Interaction) -> None:
        dad_jokes_dict = {
            "I'm afraid for the calendar.": "Its days are numbered!",
            "I used to play piano by ear,": "but now I use my hands!",
            "Why don't skeletons fight each other?": "They don't have the guts!",
            "What does a bee use to brush its hair?": "A honeycomb!",
            "Why did the scarecrow win an award?": "Because he was outstanding in his field!",
            "I only know 25 letters of the alphabet.": "I don't know y!",
            "How does a penguin build its house?": "Igloos it together!",
            "I told my wife she was drawing her eyebrows too high.": "She looked surprised!",
            "Why do scientists not trust atoms?": "Because they make up everything!",
            "What do you call fake spaghetti?": "An impasta!",
            "Want to hear a joke about construction?": "I'm still working on it!",
            "Why did the math book look sad?": "Because it had too many problems!",
            "I told my computer I needed a break,": "and now it won't stop sending me Kit-Kats!",
            "How do you organize a space party?": "You planet!",
            "I used to hate facial hair,": "but then it grew on me!",
            "Why did the coffee file a police report?": "It got mugged!",
            "Why don't eggs tell jokes?": "They'd crack each other up!",
            "How many tickles does it take to make an octopus laugh?": "Ten-tickles!",
            "Why do cows have hooves instead of feet?": "Because they lactose!",
            "Why did the golfer bring extra pants?": "In case he got a hole in one!"
        }
        joke_setup, joke_punchline = random.choice(list(dad_jokes_dict.items()))
        embed = discord.Embed(
            title = joke_setup,
            description = f":man_beard: **{joke_punchline}**",
            color = discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clapback", description="Claps back to you")
    async def clapback(self, interaction: discord.Interaction, clapsentence: str) -> None:
        clapwords = clapsentence.split()
        clap = ":clap:"
        out = clap + " " + f" {clap} ".join(clapwords) + " " + clap
        embed = discord.Embed(
            title="Serena clapped back at you!",
            description = out,
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fun(bot))