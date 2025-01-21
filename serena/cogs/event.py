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
from datetime import datetime, timezone

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

class event(commands.GroupCog, name="event", description="Event commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="transfer", description="Transfer from this room to another")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def transfer(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:
        guild = interaction.guild
        target_channel = guild.get_channel(channel.id)

        if target_channel is None or target_channel.type != discord.ChannelType.voice:
            await interaction.response.send_message("Invalid or non-voice channel provided.", ephemeral=True)
            return

        # Move members from author's voice channel to the target channel
        for member in interaction.channel.members:
            await member.move_to(target_channel)

        await interaction.response.send_message(f"Users moved to {target_channel.mention} successfully.")

    @app_commands.command(name="lock", description="Lock the event channels and turn off connection/message permissions")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def lock(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        role_ids = [1232269725841489972, 1241396492514623588]
        channel_ids = [1235213602286338128, 1236709700473585676, 1236656633669615726]
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        overwrite.send_messages = False
        overwrite.connect = False

        for channel_id in channel_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                for role_id in role_ids:
                    role = guild.get_role(role_id)
                    if role:
                        await channel.set_permissions(role, overwrite=overwrite)

        await interaction.response.send_message("Event channels locked successfully.")

    @app_commands.command(name="unlock", description="Unlock the event channels and turn on connection/message permissions")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def unlock(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        role_ids = [1232269725841489972, 1241396492514623588]
        channel_ids = [1235213602286338128, 1236709700473585676, 1236656633669615726]
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        overwrite.send_messages = True
        overwrite.connect = True

        for channel_id in channel_ids:
            channel = guild.get_channel(channel_id)
            if channel:
                for role_id in role_ids:
                    role = guild.get_role(role_id)
                    if role:
                        await channel.set_permissions(role, overwrite=overwrite)

        await interaction.response.send_message("Event channels unlocked successfully.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(event(bot))
        