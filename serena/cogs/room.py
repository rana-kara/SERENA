import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog
import json
import sqlite3
from discord import ButtonStyle
import discord.ui
import asyncio
from datetime import datetime, timezone, timedelta
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

bot = commands.Bot(prefix, intents=intents)

# Helper function to load room data
def load_room_data():
    try:
        with open("room.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Helper function to save room data
def save_room_data(data):
    with open("room.json", "w") as file:
        json.dump(data, file, indent=4)

class room(commands.GroupCog, name="room", description="Private voice channel commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="create", description="Create a private voice channel")
    async def create(self, interaction: discord.Interaction) -> None:

        # Check if the command is being used in the correct channel
        if interaction.channel_id != 1230613444827283516:
            await interaction.response.send_message("This command can only be used in <#1230613444827283516>.", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        room_data = load_room_data()

        # Count the number of rooms owned by the user
        user_rooms = [room for room in room_data.values() if room['owner'] == user_id]

        # Check if the user already owns 2 private rooms
        if len(user_rooms) >= 2:
            await interaction.response.send_message("You already own 2 private rooms!", ephemeral=True)
            return

        # Proceed to create a voice channel
        category_id = 1236866824331595788  # Replace with your category ID
        category = interaction.guild.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Category not found.", ephemeral=True)
            return

        # Create the voice channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.guild.get_role(1232269725841489972): discord.PermissionOverwrite(view_channel=True, connect=False),
            interaction.guild.get_role(1241396492514623588): discord.PermissionOverwrite(view_channel=True, connect=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        }

        new_channel = await category.create_voice_channel(
            name=f"{interaction.user.name}",
            overwrites=overwrites
        )

        # Update the room data
        room_data[new_channel.id] = {
            "owner": user_id,
            "speaking_permissions": False,
            "moderators": []
        }
        save_room_data(room_data)

        embed = discord.Embed(
            title=f"Private voice channel successfully created! <a:cutestar:1236936244722925609>",
            description="Keep in mind that your room might get deleted if the staff observe that you haven't been using it.",
            color = discord.Color(0x2B2D31)
        )

        # Respond to the user
        await interaction.response.send_message(embed=embed)    
    

        embed2 = discord.Embed(
            title=f"Welcome, {interaction.user.display_name}! <a:cutestar:1236936244722925609>",
            description="Here is a list of commands:",
            color = discord.Color(0x2B2D31)
        )
        embed2.add_field(name="/room invite", value=f"Lets you invite your friends to your room", inline=False)
        embed2.add_field(name="/room togglestudy", value=f"Toggles study mode on or off in your room", inline=False)
        embed2.add_field(name="/room delete", value=f"Lets you delete your room", inline=False)
        embed2.add_field(name="/room transfer", value=f"Lets you transfer ownership of your room", inline=False)
        embed2.add_field(name="/room makemod", value=f"Lets you make your friend a moderator in your room", inline=False)
        embed2.add_field(name="/room selfdemote", value=f"Lets you demote yourself, if you are a moderator", inline=False)
        embed2.add_field(name="/room leave", value=f"Lets you leave this room", inline=False)
        embed2.add_field(name="/room demote", value=f"Lets you demote your (ex) friend in your room", inline=False)
        embed2.add_field(name="/room rename", value=f"Lets you rename your room", inline=False)
        embed2.add_field(name="/room kick", value=f"Lets you kick your (ex) friend from your room", inline=False)
        embed2.add_field(name="/room mods", value=f"Lists all room members with moderation permissions", inline=False)
        embed2.add_field(name="/room members", value=f"Lists all room members", inline=False)
        embed2.add_field(name="/room memberping", value=f"Mentions all room members", inline=False)
        embed2.add_field(name="/room enablespeak", value=f"Enables speaking permissions for all room members", inline=False)
        embed2.add_field(name="/room disablespeak", value=f"Disables speaking permissions for all room members except the owner and the moderators", inline=False)
        embed2.add_field(name="Keep in mind that users can send join requests. Only the owner and the moderators can approve or decline.", value=" ", inline=False)

        await new_channel.send(f"{interaction.user.mention}", embed=embed2)
    
    @app_commands.command(name="makemod", description="Lets you make your friend a moderator in your room")
    async def makemod(self, interaction: discord.Interaction, user: discord.Member) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns
        if channel_id not in room_data or room_data[channel_id]["owner"] != user_id:
            await interaction.response.send_message("You can only use this command in a room you own.", ephemeral=True)
            return

        # Add the specified user to the moderators list
        if user.id not in room_data[channel_id]["moderators"]:
            room_data[channel_id]["moderators"].append(str(user.id))
            save_room_data(room_data)

            # Update channel permissions
            await interaction.channel.set_permissions(user, view_channel=True, connect=True, speak=True)

            embed = discord.Embed(
            title=f"Moderator Added <a:cutestar:1236936244722925609>",
            description=f"{user.mention} is now a moderator. She can use all room commands except `/room makemod`, `/room rename`, and `/room delete`.",
            color = discord.Color(0x2B2D31)
            )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{user.mention} is already a moderator.", ephemeral=True)

    @app_commands.command(name="demote", description="Lets you demote your (ex) friend in your room")
    async def demote(self, interaction: discord.Interaction, user: discord.Member) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns
        if channel_id not in room_data or room_data[channel_id]["owner"] != user_id:
            await interaction.response.send_message("You can only use this command in a room you own.", ephemeral=True)
            return

        # Remove the specified user from the moderators list
        if str(user.id) in room_data[channel_id]["moderators"]:
            room_data[channel_id]["moderators"].remove(str(user.id))

            # Update speaking permissions
            speak_permission = room_data[channel_id]["speaking_permissions"]
            await interaction.channel.set_permissions(user, speak=speak_permission, connect=True)

            save_room_data(room_data)

            embed = discord.Embed(
                title=f"Moderator Demoted <a:cutestar:1236936244722925609>",
                description=f"{user.mention} has been demoted. Her permissions have been updated accordingly.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{user.mention} is not a moderator.", ephemeral=True)

    @app_commands.command(name="selfdemote", description="Demote yourself from moderator position in this room")
    async def selfdemote(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the room exists in room data
        if channel_id not in room_data:
            await interaction.response.send_message("This is not a custom room. You can only use this command in custom rooms.", ephemeral=True)
            return

        # Check if the user is a moderator in this room
        if user_id in room_data[channel_id]["moderators"]:
            room_data[channel_id]["moderators"].remove(user_id)

            # Update speaking permissions
            speak_permission = room_data[channel_id]["speaking_permissions"]
            await interaction.channel.set_permissions(interaction.user, speak=speak_permission, connect=True)

            save_room_data(room_data)

            embed = discord.Embed(
                title=f"Demoted Yourself <a:cutestar:1236936244722925609>",
                description=f"{interaction.user.mention}, you have been demoted from moderator position in this room.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You are not a moderator in this room.", ephemeral=True)

    @app_commands.command(name="transfer", description="Transfer ownership of the room to another member")
    async def transfer(self, interaction: discord.Interaction, user: discord.Member) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the interaction user is the owner of the room
        if channel_id not in room_data or room_data[channel_id]["owner"] != user_id:
            await interaction.response.send_message("You can only transfer ownership in a room you own.", ephemeral=True)
            return

        old_owner_id = room_data[channel_id]["owner"]

        # Remove the old owner ID from room data
        del room_data[channel_id]["owner"]

        # Remove the new owner from the moderators list if present
        if str(user.id) in room_data[channel_id]["moderators"]:
            room_data[channel_id]["moderators"].remove(str(user.id))

        # Append the new owner ID to room data
        room_data[channel_id]["owner"] = str(user.id)

        # Transfer speaking permissions from old owner to new owner
        speak_permission = room_data[channel_id]["speaking_permissions"]
        await interaction.channel.set_permissions(interaction.user, speak=speak_permission, connect=True)
        await interaction.channel.set_permissions(user, speak=True, connect=True)

        save_room_data(room_data)

        embed = discord.Embed(
            title="Ownership Transferred <a:cutestar:1236936244722925609>",
            description=f"The ownership of the room has been transferred from <@{old_owner_id}> to {user.mention}.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rename", description="Lets you rename your room")
    async def rename(self, interaction: discord.Interaction, name: str) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns
        if channel_id not in room_data or room_data[channel_id]["owner"] != user_id:
            await interaction.response.send_message("You can only use this command in a room you own.", ephemeral=True)
            return

        # Rename the channel
        await interaction.channel.edit(name=name)

        embed = discord.Embed(
            title=f"Room Renamed <a:cutestar:1236936244722925609>",
            description=f"Your room has been renamed to {name}.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="delete", description="Delete your room")
    async def delete(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)
        role_id = 1233423130521768028  # Replace with the actual role ID to check
        guild = interaction.guild
        role = guild.get_role(role_id)

        # Check if the command is being invoked in a room the user owns
        if channel_id not in room_data or room_data[channel_id]["owner"] != user_id:
            if role not in interaction.user.roles:
                await interaction.response.send_message("You can only use this command in a room you own.", ephemeral=True)
                return

        embed = discord.Embed(
            title="Room Deletion in Progress <a:cutestar:1236936244722925609>",
            description="Your room will be deleted in 5 seconds.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

        # Wait for 5 seconds
        await asyncio.sleep(5)

        # Delete the channel
        await interaction.channel.delete()

        # Remove the room data
        del room_data[channel_id]
        save_room_data(room_data)

    @app_commands.command(name="invite", description="Invite your friend to your room")
    async def invite(self, interaction: discord.Interaction, user: discord.Member) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns or if the user is a moderator
        if channel_id not in room_data or (room_data[channel_id]["owner"] != user_id and str(user_id) not in room_data[channel_id]["moderators"]):
            await interaction.response.send_message("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        # Check if the user already has permission to connect
        existing_permissions = interaction.channel.permissions_for(user)
        if existing_permissions.connect:
            await interaction.response.send_message(f"{user.mention} already has permission to connect to the channel.", ephemeral=True)
            return

        # Fetch speaking permissions from room data
        speak_permission = room_data[channel_id]["speaking_permissions"]

        # Update channel permissions for the invited user
        await interaction.channel.set_permissions(user, view_channel=True, connect=True, speak=speak_permission)

        embed = discord.Embed(
            title="User Invited <a:cutestar:1236936244722925609>",
            description=f"{user.mention} has been invited to the room.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(f"{user.mention}", embed=embed)

    @app_commands.command(name="kick", description="Lets you kick a member from your room")
    async def kick(self, interaction: discord.Interaction, user: discord.Member) -> None:
        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns or if the user is a moderator
        if channel_id not in room_data or (room_data[channel_id]["owner"] != user_id and str(user_id) not in room_data[channel_id]["moderators"]):
            await interaction.response.send_message("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        # Remove the user from the channel
        await interaction.channel.set_permissions(user, overwrite=None)

        embed = discord.Embed(
            title="User Kicked <a:cutestar:1236936244722925609>",
            description=f"{user.mention} has been kicked from the room.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leave", description="Lets you leave this room")
    async def leave(self, interaction: discord.Interaction) -> None:
        user = interaction.user
        user_id = str(user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a private room
        if channel_id not in room_data:
            await interaction.response.send_message("This isn't a private room that you can leave.", ephemeral=True)
            return
        
        if room_data[channel_id]["owner"] == user_id:
            await interaction.response.send_message("You own this room. You can't leave it without deleting it or transferring ownership.", ephemeral=True)
            return
        
        if user_id in room_data[channel_id]["moderators"]:
            await interaction.response.send_message("You moderate this room. Demote yourself first by doing `/room selfdemote` in this channel.", ephemeral=True)
            return

        # Remove the user from the channel permissions
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message("You have successfully left the channel.", ephemeral=True)

    @app_commands.command(name="mods", description="See all moderators of this channel")
    async def mods(self, interaction: discord.Interaction) -> None:
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        if channel_id not in room_data:
            await interaction.response.send_message("No moderators found for this channel.")
            return

        moderators = room_data[channel_id].get("moderators", [])
        if moderators:
            moderators_mentions = [f"<@{moderator_id}>" for moderator_id in moderators]
            embed = discord.Embed(
                title="Moderators of This Room <a:cutestar:1236936244722925609>",
                description="Here are the moderators of this channel:",
                color = discord.Color(0x2B2D31)
            )
            embed.add_field(name="Moderators", value="\n".join(moderators_mentions), inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No moderators found for this channel.")

    @app_commands.command(name="members", description="See all members of this channel")
    async def members(self, interaction: discord.Interaction) -> None:
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)
        if channel_id not in room_data:
            await interaction.response.send_message("This is not a custom room. You can only use this command in custom rooms.", ephemeral=True)
            return

        channel = interaction.channel
        room_info = room_data[channel_id]

        owner_id = room_info.get("owner")
        owner_mention = f"<@{owner_id}>" if owner_id else "No owner found"

        moderators = room_info.get("moderators", [])
        moderator_mentions = [f"<@{moderator_id}>" for moderator_id in moderators]

        # Get members with connect permissions
        advanced_members = set()
        for member in channel.overwrites:
            if isinstance(member, discord.Member):
                perms = channel.permissions_for(member)
                if perms.connect:
                    advanced_members.add(member.mention)

        for role in channel.overwrites:
            if isinstance(role, discord.Role):
                perms = channel.permissions_for(role)
                if perms.connect:
                    for member in role.members:
                        member_perms = channel.permissions_for(member)
                        if member_perms.connect:
                            advanced_members.add(member.mention)

        advanced_members = list(advanced_members)

        embed = discord.Embed(
            title="Room Members <a:cutestar:1236936244722925609>",
            description="List of members with roles and permissions in this channel",
            color = discord.Color(0x2B2D31)
        )
        embed.add_field(name="Owner", value=owner_mention, inline=False)
        embed.add_field(name="Moderators", value="\n".join(moderator_mentions) if moderator_mentions else "No moderators", inline=False)
        embed.add_field(name="Members with Connect Permissions", value="\n".join(advanced_members) if advanced_members else "No members with connect permissions", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="memberping", description="Ping all the members in this channel")
    async def memberping(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        channel_id = str(interaction.channel.id)
        room_data = load_room_data()
        if channel_id not in room_data:
            await interaction.response.send_message("This is not a custom room. You can only use this command in custom rooms.", ephemeral=True)
            return
        
        if (room_data[channel_id]["owner"] != user_id and str(user_id) not in room_data[channel_id]["moderators"]):
            await interaction.response.send_message("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        channel = interaction.channel
        advanced_members = set()

        # Check explicit member overwrites
        for member in channel.overwrites:
            if isinstance(member, discord.Member):
                perms = channel.permissions_for(member)
                if perms.connect:
                    advanced_members.add(member.mention)

        # Check role overwrites and add members with those roles
        for role in channel.overwrites:
            if isinstance(role, discord.Role):
                perms = channel.permissions_for(role)
                if perms.connect:
                    for member in role.members:
                        member_perms = channel.permissions_for(member)
                        if member_perms.connect:
                            advanced_members.add(member.mention)

        # Collecting all mentions
        advanced_members = list(advanced_members)

        if not advanced_members:
            await interaction.response.send_message("No members with connection permissions found in this channel.", ephemeral=True)
            return

        ping_message = " ".join(advanced_members)
        await interaction.response.send_message(ping_message)

    @app_commands.command(name="enablespeak", description="Enables speaking permissions for a member or all members.")
    @app_commands.describe(user="The user to enable speaking permissions for. If not provided, enables for all members.")
    async def enablespeak(self, interaction: discord.Interaction, user: Optional[discord.Member] = None) -> None:
        # Defer the response to avoid timeout errors
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)
        room_data = load_room_data()  # Load room data
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked by the owner of the room or a moderator
        if channel_id not in room_data or (room_data[channel_id]["owner"] != user_id and user_id not in room_data[channel_id]["moderators"]):
            await interaction.followup.send("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        if user:
            # Update permissions for the specified user
            current_overwrite = interaction.channel.overwrites_for(user)
            current_overwrite.update(speak=True)
            await interaction.channel.set_permissions(user, overwrite=current_overwrite)
            embed_description = f"{user.mention} now has speaking permissions in this channel."
        else:
            # Update permissions for all members
            for target in interaction.channel.overwrites:
                if isinstance(target, discord.Member):
                    current_overwrite = interaction.channel.overwrites_for(target)
                    current_overwrite.update(speak=True)
                    await interaction.channel.set_permissions(target, overwrite=current_overwrite)
            embed_description = "All members now have speaking permissions in this channel."

        # Update the room_data with the new speaking permissions setting
        room_data[channel_id]["speaking_permissions"] = True
        save_room_data(room_data)  # Save the updated room data

        embed = discord.Embed(
            title="Speaking Permissions Enabled <a:cutestar:1236936244722925609>",
            description=embed_description,
            color = discord.Color(0x2B2D31)
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="disablespeak", description="Disables speaking permissions for a member or all members (except the owner and the mods)")
    @app_commands.describe(user="The user to disable speaking permissions for. If not provided, disables for all members except the owner and mods.")
    async def disablespeak(self, interaction: discord.Interaction, user: Optional[discord.Member] = None) -> None:
        # Defer the response to avoid timeout errors
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a room the user owns or moderates
        if channel_id not in room_data or (room_data[channel_id]["owner"] != user_id and user_id not in room_data[channel_id]["moderators"]):
            await interaction.followup.send("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        if user:
            if str(user.id) == room_data[channel_id]["owner"] or str(user.id) in room_data[channel_id]["moderators"]:
                await interaction.followup.send("Room owners or moderators cannot be muted.", ephemeral=True)
                return  # Exit the command if the target user is the owner or a moderator
                            
            # Disable speaking permissions for the specified user
            current_overwrite = interaction.channel.overwrites_for(user)
            current_overwrite.update(speak=False)
            await interaction.channel.set_permissions(user, overwrite=current_overwrite)
            embed_description = f"{user.mention} now has their speaking permissions disabled in this channel."
        else:
            # Disable speaking permissions for all regular members (except the owner and mods)
            for target in interaction.channel.overwrites:
                if isinstance(target, discord.Member) and str(target.id) != room_data[channel_id]["owner"] and str(target.id) not in room_data[channel_id]["moderators"]:
                    current_overwrite = interaction.channel.overwrites_for(target)
                    current_overwrite.update(speak=False)
                    await interaction.channel.set_permissions(target, overwrite=current_overwrite)
            embed_description = "Speaking permissions have been disabled for all members (except the owner and mods) in this channel."

        # Update the room_data with the new speaking permissions setting
        room_data[channel_id]["speaking_permissions"] = False
        save_room_data(room_data)  # Save the updated room data

        embed = discord.Embed(
            title="Speaking Permissions Disabled <a:cutestar:1236936244722925609>",
            description=embed_description,
            color = discord.Color(0x2B2D31)
        )
        await interaction.followup.send(embed=embed)



    @app_commands.command(name="request", description="Request to join a private voice channel")
    async def request(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:
        guild = interaction.guild
        target_channel = guild.get_channel(channel.id)
        user = interaction.user
        room_data = load_room_data()
        current_channel_id = str(channel.id)

        # Check if the channel is in the room data
        if current_channel_id not in room_data:
            await interaction.response.send_message("That's not a private room! Please choose a valid private room.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Join Request <a:cutestar:1236936244722925609>",
            description=f"{user.mention} has requested to join this channel. Do you accept?"
        )

        class AcceptDecline(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
            async def accept_button(self, button_interaction: discord.Interaction, button: discord.ui.button):
                button_user_id = str(button_interaction.user.id)
                # Check if the command is being invoked in a room the user owns or if the user is a moderator
                if (room_data[current_channel_id]["owner"] != button_user_id and button_user_id not in room_data[current_channel_id]["moderators"]):
                    await button_interaction.response.send_message("You can't accept or decline because you are not an owner or a moderator in this room.", ephemeral=True)
                    return
                else:
                    # Fetch speaking permissions from room data
                    speak_permission = room_data[current_channel_id]["speaking_permissions"]

                    # Update channel permissions for the invited user
                    await button_interaction.channel.set_permissions(user, view_channel=True, connect=True, speak=speak_permission)

                    embed = discord.Embed(
                        title="Request Accepted <a:cutestar:1236936244722925609>",
                        color = discord.Color(0x2B2D31)
                    )
                    await button_interaction.response.send_message(f"Welcome, {user.mention}!", embed=embed)

                    # Remove all buttons after accepting
                    self.clear_items()

            @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger)
            async def decline_button(self, button_interaction: discord.Interaction, button: discord.ui.button):
                embed = discord.Embed(
                    title="Request Declined <a:cutestar:1236936244722925609>",
                    color=discord.Color.red()
                )
                await button_interaction.response.send_message(embed=embed)

                # Remove all buttons after declining
                self.clear_items()

        view = AcceptDecline()
        await target_channel.send(embed=embed, view=view)
        await interaction.response.send_message("Your request has been sent to the room.", ephemeral=True)

    @app_commands.command(name="status", description="Information about this room")
    async def status(self, interaction: discord.Interaction) -> None:
        room_data = load_room_data()
        channel_id = str(interaction.channel.id)

        # Check if the command is being invoked in a valid room
        if channel_id not in room_data:
            await interaction.response.send_message("This is not a custom room. You can only use this command in custom rooms.", ephemeral=True)
            return

        room_info = room_data[channel_id]

        # Fetch owner and moderators information
        owner_mention = f"<@{room_info['owner']}>"
        moderators_mentions = [f"<@{mod_id}>" for mod_id in room_info['moderators']]
        moderators_value = "\n".join(moderators_mentions) if moderators_mentions else "No moderators"

        # Count members with connection permissions
        connected_members = 0
        for target in interaction.channel.overwrites:
            if isinstance(target, discord.Member):
                perms = interaction.channel.permissions_for(target)
                if perms.connect:
                    connected_members += 1

        # Check if speaking permissions are enabled
        speaking_permissions_status = "Enabled" if room_info.get("speaking_permissions", False) else "Disabled"

        # Check if study mode is enabled
        study_mode_status = "On" if room_info.get("monitored") == "Yes" else "Off"

        # Create the embed
        embed = discord.Embed(
            title=f"Room Status - {interaction.channel.name} <a:cutestar:1236936244722925609>",
            color = discord.Color(0x2B2D31)
        )
        embed.add_field(name="Owner", value=owner_mention, inline=False)
        embed.add_field(name="Moderators", value=moderators_value, inline=False)
        embed.add_field(name="Members With Connection Permissions", value=str(connected_members), inline=False)
        embed.add_field(name="Speaking Permissions", value=speaking_permissions_status, inline=False)
        embed.add_field(name="Study Mode", value=study_mode_status, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="togglestudy", description="Turn on study mode for this room")
    async def togglestudy(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        channel_id = str(interaction.channel.id)
        room_data = load_room_data()

        # Check if the command is being invoked in a room the user owns or moderates
        if channel_id not in room_data or (room_data[channel_id]["owner"] != user_id and user_id not in room_data[channel_id]["moderators"]):
            await interaction.response.send_message("You can only use this command in a room you own or moderate.", ephemeral=True)
            return

        # Toggle the study mode
        if "monitored" in room_data[channel_id]:
            if room_data[channel_id]["monitored"] == "Yes":
                room_data[channel_id]["monitored"] = "No"
                status_message = "Study mode is now **disabled**. Your time in this room will no longer be tracked."
                color = discord.Color(0x2B2D31)
            else:
                room_data[channel_id]["monitored"] = "Yes"
                status_message = "Study mode is now **enabled**. Your time in this room will be tracked."
                color = discord.Color(0x2B2D31)
        else:
            room_data[channel_id]["monitored"] = "Yes"
            status_message = "Study mode is now **enabled**. Your time in this room will be tracked."
            color = discord.Color(0x2B2D31)

        # Save the updated room data
        save_room_data(room_data)

        embed = discord.Embed(
            title="Study Mode Toggled <a:cutestar:1236936244722925609>",
            description=status_message,
            color=color
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(room(bot))