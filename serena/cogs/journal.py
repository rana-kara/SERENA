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


class journal(commands.GroupCog, name="journal", description="Journal commands."):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="delete", description="Delete your journal")
    async def delete(self, interaction: discord.Interaction):

        # Check if the invoker is the author of the forum post (thread)
        post = interaction.channel
        if not isinstance(post, discord.Thread):
            await interaction.response.send_message(
                embed=discord.Embed(description="This command can only be used in a forum post.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        if interaction.user.id != post.owner_id:
            await interaction.response.send_message(
                embed=discord.Embed(description="You can only use this in a post you are the OP of.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        # Notify the deletion
        await interaction.response.send_message(
            embed=discord.Embed(description="This journal will be deleted in 5 seconds.", color = discord.Color(0x2B2D31))
        )

        # Wait for 5 seconds before deletion
        await asyncio.sleep(5)

        # Delete the post (thread)
        await post.delete()

    @app_commands.command(name="pin", description="Pin a message in your journal")
    async def pin(self, interaction: discord.Interaction, message_id: str):

        # Check if the invoker is the author of the forum post (thread)
        post = interaction.channel
        if not isinstance(post, discord.Thread):
            await interaction.response.send_message(
                embed=discord.Embed(description="This command can only be used in a forum post.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        if interaction.user.id != post.owner_id:
            await interaction.response.send_message(
                embed=discord.Embed(description="You can only use this in a post you are the OP of.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        try:
            # Fetch the message by ID
            message = await post.fetch_message(int(message_id))
            # Pin the message
            await message.pin()
            # Send success message
            await interaction.response.send_message(
                embed=discord.Embed(description="Message successfully pinned! <a:cutestar:1236936244722925609>", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                embed=discord.Embed(description="Message not found.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                embed=discord.Embed(description=f"Failed to pin the message: {e}", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )

    @app_commands.command(name="unpin", description="Unpin a message in your journal")
    async def unpin(self, interaction: discord.Interaction, message_id: str):

        # Check if the invoker is the author of the forum post (thread)
        post = interaction.channel
        if not isinstance(post, discord.Thread):
            await interaction.response.send_message(
                embed=discord.Embed(description="This command can only be used in a forum post.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        if interaction.user.id != post.owner_id:
            await interaction.response.send_message(
                embed=discord.Embed(description="You can only use this in a post you are the OP of.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            return

        try:
            # Fetch the message by ID
            message = await post.fetch_message(int(message_id))
            # Unpin the message
            await message.unpin()
            # Send success message
            await interaction.response.send_message(
                embed=discord.Embed(description="Message successfully unpinned! <a:cutestar:1236936244722925609>", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
        except discord.NotFound:
            await interaction.response.send_message(
                embed=discord.Embed(description="Message not found.", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                embed=discord.Embed(description=f"Failed to unpin the message: {e}", color = discord.Color(0x2B2D31)),
                ephemeral=True
            )
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(journal(bot))