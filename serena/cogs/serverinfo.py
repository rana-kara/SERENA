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

class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Displays information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild

        embed = discord.Embed(
            title=f"<a:cutestar:1236936244722925609> Server Information - {guild.name} <a:cutestar:1236936244722925609>",
            color = discord.Color(0x2B2D31)
        )
        embed.set_thumbnail(url=guild.icon.url)

        # General Info
        embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
        embed.add_field(name="ID", value=guild.id, inline=False)
        embed.add_field(name="Region", value=str(guild.preferred_locale), inline=False)
        embed.add_field(name="Created", value=f"{guild.created_at.strftime('%B %d, %Y')} ({discord.utils.format_dt(guild.created_at, style='R')})", inline=False)
        embed.add_field(name="Verification Level", value=str(guild.verification_level).capitalize(), inline=False)
        embed.add_field(name="Vanity URL", value=guild.vanity_url_code if guild.vanity_url_code else "/None", inline=False)

        # Member Info
        embed.add_field(name="Member Info", value=f"Total Members: {guild.member_count}\nHumans: {len([m for m in guild.members if not m.bot])}\nBots: {len([m for m in guild.members if m.bot])}", inline=True)

        # Emojis Info
        # Emojis Info
        animated_emojis = [emoji for emoji in guild.emojis if emoji.animated]
        static_emojis = [emoji for emoji in guild.emojis if not emoji.animated]
        embed.add_field(name="Emojis", value=f"Static Emojis: {len(static_emojis)}\nAnimated Emojis: {len(animated_emojis)}\nTotal Emojis: {len(guild.emojis)}", inline=True)

        # Channels Info
        embed.add_field(name="Channels", value=f"Text Channels: {len(guild.text_channels)}\nVoice Channels: {len(guild.voice_channels)}\nCategories: {len(guild.categories)}", inline=True)

        # Roles Info
        embed.add_field(name="Roles", value=f"Total Roles: {len(guild.roles)}", inline=True)

        # Stickers Info
        embed.add_field(name="Stickers", value=f"Total Stickers: {len(guild.stickers)}", inline=True)

        # Boost Status
        embed.add_field(name="Boost Status", value=f"Level: {guild.premium_tier}\nBoosts: {guild.premium_subscription_count}\nBoosters: {len(guild.premium_subscribers)}", inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(serverinfo(bot))