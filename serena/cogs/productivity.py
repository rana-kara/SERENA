import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
import json
import sqlite3
from discord import ButtonStyle
import discord.ui
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

class status(commands.GroupCog, name="status", description="Set a status"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="focus", description="Hides non-study related channels")
    async def focus(self, interaction: discord.Interaction) -> None:
        focus_role_id = 1241396492514623588
        non_focus_role_id = 1232269725841489972

        # Check if the user has neither role
        if not any(role.id in [focus_role_id, non_focus_role_id] for role in interaction.user.roles):
            await interaction.response.send_message("You're not verified, you can't use this command!", ephemeral=True)
            return

        # Check if the user already has the focus role
        if any(role.id == focus_role_id for role in interaction.user.roles):
            await interaction.response.send_message("You're already in deep focus mode!", ephemeral=True)
            return

        # Proceed with the command if the user does not have the focus role
        embed = discord.Embed(
            title=f"Good luck with your work, {interaction.user.display_name}! <a:cutestar:1236936244722925609>",
            description="This user has set their status to **focus**. They can't see non-study related channels.",
            color = discord.Color(0x2B2D31)
        )

        await interaction.user.add_roles(discord.Object(id=focus_role_id))
        await interaction.user.remove_roles(discord.Object(id=non_focus_role_id))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unfocus", description="Reveals non-study related channels")
    async def unfocus(self, interaction: discord.Interaction) -> None:
        focus_role_id = 1241396492514623588
        non_focus_role_id = 1232269725841489972

        # Check if the user has neither role
        if not any(role.id in [focus_role_id, non_focus_role_id] for role in interaction.user.roles):
            await interaction.response.send_message("You're not verified, you can't use this command!", ephemeral=True)
            return

        # Check if the user already has the non-focus role
        if any(role.id == non_focus_role_id for role in interaction.user.roles):
            await interaction.response.send_message("You're not in deep focus mode, you can't unfocus!", ephemeral=True)
            return

        # Proceed with the command if the user does not have the non-focus role
        embed = discord.Embed(
            title=f"I hope you had a productive session, {interaction.user.display_name}! <a:cutestar:1236936244722925609>",
            description="This user has removed their focus status. They can now see all channels.",
            color = discord.Color(0x2B2D31)
        )

        await interaction.user.add_roles(discord.Object(id=non_focus_role_id))
        await interaction.user.remove_roles(discord.Object(id=focus_role_id))
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(status(bot))
