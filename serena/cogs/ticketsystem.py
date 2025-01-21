import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
import json
import sqlite3
import asyncio
import  datetime
from typing import Optional
import os
import json

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

def load_verification_data():
    if os.path.exists("verifications.json"):
        with open("verifications.json", "r") as f:
            return json.load(f)
    return {}

def save_verification_data(data):
    with open("verifications.json", "w") as f:
        json.dump(data, f, indent=4)

class ticketsystem(commands.GroupCog, name="verification", description="Verify a user"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    def get_suffix(self, number):
        if 10 <= number % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

    @app_commands.command(name="verify", description="Verify a user")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def verify(self, interaction: discord.Interaction, user: discord.Member) -> None:

        role1 = interaction.guild.get_role(1232269725841489972)
        role2 = interaction.guild.get_role(1241396492514623588)
        member_count = len(role1.members) + len(role2.members) + 1  # Add members of both roles and add 1 for the new user
        suffix = self.get_suffix(member_count)

        embed = discord.Embed(
            title="Welcome to ***Girls Only*** .ᐟ",
            description="<a:cutestar:1236936244722925609> Get some [roles](https://discord.com/channels/1230594017847414784/1247105321361604661)\n<a:cutestar:1236936244722925609> Read the [rules](https://discord.com/channels/1230594017847414784/1230594019050918009)\n<a:cutestar:1236936244722925609> Introduce yourself in [introductions](https://discord.com/channels/1230594017847414784/1232290868262867035)\n<a:cutestar:1236936244722925609> Check out [faq](https://discord.com/channels/1230594017847414784/1247573775281688728) for more!",
            color = discord.Color(0x2B2D31)
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"You are our {member_count}{suffix} verified member!")

        verification_channel = interaction.guild.get_channel(1230594019625795687)

        await user.add_roles(discord.Object(id=1232269725841489972))

        if verification_channel:
            await verification_channel.send(content=user.mention, embed=embed)
            success_embed = discord.Embed(
                title="Welcome message was sent to the channel. The user is verified and the ticket will be deleted within 5 seconds.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=success_embed)
        else:
            fail_embed = discord.Embed(
                title="Failed to find the verification channel. The user is verified, and the ticket will be deleted in 5 seconds.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=fail_embed)

        data = load_verification_data()
        staff_id = str(interaction.user.id)
        if staff_id in data:
            data[staff_id] += 1
        else:
            data[staff_id] = 1
        save_verification_data(data)

        # Load the open tickets data
        try:
            with open('opentickets.json', 'r') as file:
                open_tickets = json.load(file)
        except FileNotFoundError:
            open_tickets = {}

        # Find the user ID corresponding to this channel
        user_id = None
        for uid, cid in open_tickets.items():
            if cid == interaction.channel.id:
                user_id = uid
                break

        # Remove the user ID and channel ID from the open tickets data
        if user_id:
            del open_tickets[user_id]
            with open('opentickets.json', 'w') as file:
                json.dump(open_tickets, file, indent=4)

        await asyncio.sleep(5)
        await interaction.channel.delete()

    @app_commands.command(name="leaderboard", description="Show verification leaderboard")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        data = load_verification_data()
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

        leaderboard = "\n".join([f"<@{user_id}>: {count}" for user_id, count in sorted_data[:20]])
        if not leaderboard:
            leaderboard = "No verifications yet."
            
        embed = discord.Embed(
            title="Verification Leaderboard <a:cutestar:1236936244722925609>",
            description=leaderboard,
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unverify", description="Unverify a user")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def unverify(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        embed = discord.Embed(
        title=f"Your verification in Girls Only has been revoked. | Reason: {reason}",
        description="This is a message to inform you that you have been unverified from the server. Please wait for staff and make sure to be on the lookout for any updates on your situation.",
        color = discord.Color(0x2B2D31)
        )
        await user.send(embed=embed) 
        await user.remove_roles(discord.Object(id=1232269725841489972))
        await interaction.response.send_message(f"{user.display_name} has been unverified. Reason: {reason}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ticketsystem(bot))