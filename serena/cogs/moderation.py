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
import os
from typing import Optional

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

class close_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def this_button(self, interaction: discord.Interaction, button: discord.ui.button):
        channel = interaction.channel
        embed = discord.Embed(
            title=f"This ticket will be deleted in 5 seconds.",
            color = discord.Color(0x2B2D31))
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5) 
        await channel.delete()
    async def interaction_check(self, interaction):
        member = interaction.user
        role = discord.utils.get(member.roles, id=1233423130521768028)
        if role:
            return True
        return False
     
# Ensure that warnings.json exists
def ensure_warnings_file():
    if not os.path.exists('warnings.json'):
        with open('warnings.json', 'w') as f:
            json.dump({}, f)

# Add a warning to the warnings.json file
def add_warning(user_id: int, reason: str):
    ensure_warnings_file()

    with open('warnings.json', 'r') as f:
        warnings = json.load(f)

    if user_id not in warnings:
        warnings[user_id] = {}

    # Determine the next warning ID
    warning_ids = list(warnings[user_id].keys())
    next_warning_id = str(max([int(wid) for wid in warning_ids], default=0) + 1)

    warnings[user_id][next_warning_id] = reason

    with open('warnings.json', 'w') as f:
        json.dump(warnings, f, indent=4)

# Clear warning(s) from the warnings.json file
def clear_warning(user_id: int, warning_id: Optional[str] = None):
    ensure_warnings_file()

    with open('warnings.json', 'r') as f:
        warnings = json.load(f)

    if str(user_id) not in warnings:
        return False

    if warning_id:
        if warning_id in warnings[str(user_id)]:
            del warnings[str(user_id)][warning_id]
            if not warnings[str(user_id)]:  # if no more warnings, delete the user entry
                del warnings[str(user_id)]
        else:
            return False
    else:
        del warnings[str(user_id)]

    with open('warnings.json', 'w') as f:
        json.dump(warnings, f, indent=4)
    
    return True

# Get warnings for a user
def get_warnings(user_id: int):
    ensure_warnings_file()

    with open('warnings.json', 'r') as f:
        warnings = json.load(f)

    return warnings.get(str(user_id), {})

class moderation(commands.GroupCog, name="moderation", description="Moderation commands."):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        embed = discord.Embed(
        title=f"You have been banned from Girls Only. | Reason: {reason}",
        description="This is a message to inform you that you have been banned from the server. If you think we made a mistake, please appeal using [this link](https://forms.gle/vqwCPSoBsRuvHcvX8).",
        color = discord.Color(0x2B2D31)
        )
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass  # Ignore if the user has DMs disabled
        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"{user.display_name} has been banned successfully. Reason: {reason}") 

    @app_commands.command(name="unban", description="Unban a member")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str) -> None:
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"{user.display_name} has been unbanned successfully. Reason: {reason}") 

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str) -> None:
        embed = discord.Embed(
            title=f"You have been warned in Girls Only. | Reason: {reason}",
            description="This is a message to inform you that you have been warned. No further actions needed. If you think we made a mistake, appeal by opening a Help & Support ticket in the server.",
            color = discord.Color(0x2B2D31)
        )
        await user.send(embed=embed)
        await interaction.response.send_message(f"{user.display_name} has been warned successfully. Reason: {reason}")

        # Add warning to the JSON file
        add_warning(user.id, reason)

    @app_commands.command(name="clearwarn", description="Remove warnings from a member")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def clearwarn(self, interaction: discord.Interaction, user: discord.Member, warning_id: Optional[str] = None ) -> None:
        success = clear_warning(user.id, warning_id)
        if success:
            if warning_id:
                await interaction.response.send_message(f"Warning ID {warning_id} for {user.display_name} has been cleared successfully.")
            else:
                await interaction.response.send_message(f"All warnings for {user.display_name} have been cleared successfully.")
        else:
            await interaction.response.send_message(f"No warnings found for {user.display_name} with the provided warning ID.")
    

    @app_commands.command(name="modinfo", description="Moderation info about a member")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def modinfo(self, interaction: discord.Interaction, user: discord.Member) -> None:
        roles = [role.mention for role in user.roles]

        warnings_data = get_warnings(user.id)
        warnings_formatted = "\n".join([f"ID: {wid}, Reason: {reason}" for wid, reason in warnings_data.items()]) if warnings_data else "No warnings"

        creation_days = (datetime.now(timezone.utc) - user.created_at).days
        creation_years, creation_days = divmod(creation_days, 365)

        join_duration = datetime.now(timezone.utc) - user.joined_at
        join_years, join_days = divmod(join_duration.days, 365)
        join_hours, remainder = divmod(join_duration.seconds, 3600)
        join_minutes, _ = divmod(remainder, 60)

        embed = discord.Embed(
            title=f"{user} <a:cutestar:1236936244722925609>",
            color = discord.Color(0x2B2D31)
        )
        embed.add_field(name="Roles", value=", ".join(roles), inline=False)
        embed.add_field(name="Warnings", value=warnings_formatted, inline=False)
        embed.add_field(name="Account Creation", value=f"The account was created {creation_years} years and {creation_days} days ago.", inline=False)
        embed.add_field(name="Joined Server", value=f"They joined the server {join_years} years, {join_days} days, {join_hours} hours, {join_minutes} minutes ago.", inline=False)
        embed.set_footer(text=f"User ID: {user.id}")
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ticket", description="Create a channel private to staff and the specified user")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def ticket(self, interaction: discord.Interaction, user: discord.Member) -> None:
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(1233423130521768028): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(f"₊˚・{user.name}", overwrites=overwrites)

        embed = discord.Embed(
            title=f"You have been called here by staff.",
            description="This could be due to a various number of reasons. Please wait for further assistance.",
            color = discord.Color(0x2B2D31)
        )

        await channel.send(f"{interaction.user.mention} has summoned {user.mention}.", embed=embed, view=close_button())
        await interaction.response.send_message(f"Moderation ticket created successfully. Refer to: {channel.mention}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(moderation(bot))