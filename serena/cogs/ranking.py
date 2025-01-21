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
from datetime import datetime, timezone, timedelta
import os

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

class timezoneselectminus(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="GMT-12"),
            discord.SelectOption(label="GMT-11"),
            discord.SelectOption(label="GMT-10"),
            discord.SelectOption(label="GMT-9"),
            discord.SelectOption(label="GMT-8"),
            discord.SelectOption(label="GMT-7"),
            discord.SelectOption(label="GMT-6"),
            discord.SelectOption(label="GMT-5"),
            discord.SelectOption(label="GMT-4"),
            discord.SelectOption(label="GMT-3"),
            discord.SelectOption(label="GMT-2"),
            discord.SelectOption(label="GMT-1"),
            discord.SelectOption(label="GMT")
            ]
        super().__init__(placeholder="Select a time zone!",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_time_zone = self.values[0]  # Get the selected time zone
        user_id = str(interaction.user.id)
        ranking_file = 'ranking.json'

        # Load the ranking data from the JSON file
        if os.path.exists(ranking_file):
            with open(ranking_file, 'r') as f:
                ranking_data = json.load(f)
        else:
            ranking_data = {}

        # Ensure the user data exists
        if user_id not in ranking_data:
            ranking_data[user_id] = {}

        # Set or update the user's time zone
        ranking_data[user_id]['time_zone'] = selected_time_zone

        # Save the updated ranking data back to the JSON file
        with open(ranking_file, 'w') as f:
            json.dump(ranking_data, f, indent=4)

        # Create an embed to confirm the update
        embed = discord.Embed(
            title="Time Zone Set <a:cutestar:1236936244722925609>",
            description=f"Your time zone has been set to `{selected_time_zone}`.",
            color=discord.Color(0x2B2D31)
        )

        # Send a response with the embed
        await interaction.response.send_message(embed=embed, ephemeral=True)

class timezoneselectminusview(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(timezoneselectminus())

class timezoneselectplus(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="GMT"),
            discord.SelectOption(label="GMT+1"),
            discord.SelectOption(label="GMT+2"),
            discord.SelectOption(label="GMT+3"),
            discord.SelectOption(label="GMT+4"),
            discord.SelectOption(label="GMT+5"),
            discord.SelectOption(label="GMT+6"),
            discord.SelectOption(label="GMT+7"),
            discord.SelectOption(label="GMT+8"),
            discord.SelectOption(label="GMT+9"),
            discord.SelectOption(label="GMT+10"),
            discord.SelectOption(label="GMT+11"),
            discord.SelectOption(label="GMT+12")
            ]
        super().__init__(placeholder="Select a time zone!",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_time_zone = self.values[0]  # Get the selected time zone
        user_id = str(interaction.user.id)
        ranking_file = 'ranking.json'

        # Load the ranking data from the JSON file
        if os.path.exists(ranking_file):
            with open(ranking_file, 'r') as f:
                ranking_data = json.load(f)
        else:
            ranking_data = {}

        # Ensure the user data exists
        if user_id not in ranking_data:
            ranking_data[user_id] = {}

        # Set or update the user's time zone
        ranking_data[user_id]['time_zone'] = selected_time_zone

        # Save the updated ranking data back to the JSON file
        with open(ranking_file, 'w') as f:
            json.dump(ranking_data, f, indent=4)

        # Create an embed to confirm the update
        embed = discord.Embed(
            title="Time Zone Set <a:cutestar:1236936244722925609>",
            description=f"Your time zone has been set to `{selected_time_zone}`.",
            color=discord.Color(0x2B2D31)
        )

        # Send a response with the embed
        await interaction.response.send_message(embed=embed, ephemeral=True)

class timezoneselectplusview(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(timezoneselectplus())

def convert_gmt_to_timezone(gmt_string):
    if gmt_string == "GMT":
        return timezone.utc
    sign = -1 if '-' in gmt_string else 1
    offset_hours = int(gmt_string.replace('GMT', '').replace('+', '').replace('-', ''))
    return timezone(timedelta(hours=sign * offset_hours))

def get_user_time_zone(user_id):
    ranking_file = 'ranking.json'
    if os.path.exists(ranking_file):
        with open(ranking_file, 'r') as f:
            ranking_data = json.load(f)
        user_data = ranking_data.get(user_id)
        if user_data:
            time_zone_str = user_data.get('time_zone', 'GMT')
            return convert_gmt_to_timezone(time_zone_str)
    return timezone.utc  # Default to UTC if no time zone is set

class rank(commands.GroupCog, name="rank", description="Ranking system commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="settimezoneminus", description="Set your time zone for accurate daily study statistics (minus time zones)")
    async def settimezoneminus(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Select A Time Zone <a:cutestar:1236936244722925609>",
            description="Select your time zone below to be able to view your daily study statistics accurately.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed, view=timezoneselectminusview(), ephemeral=True)

    @app_commands.command(name="settimezoneplus", description="Set your time zone for accurate daily study statistics (plus time zones)")
    async def settimezoneplus(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Select A Time Zone <a:cutestar:1236936244722925609>",
            description="Select your time zone below to be able to view your daily study statistics accurately.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed, view=timezoneselectplusview(), ephemeral=True)

    @app_commands.command(name="reset", description="Reset the study data for this month")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def monthlyreset(self, interaction: discord.Interaction):
        ranking_file = 'ranking.json'

        # Check if the ranking.json file exists
        if os.path.exists(ranking_file):
            # Open the file and clear its contents
            with open(ranking_file, 'w') as file:
                json.dump({}, file)  # Write an empty dictionary to the file

            await interaction.response.send_message("Study data has been reset for this month.", ephemeral=True)
        else:
            await interaction.response.send_message("Ranking file not found. No data to reset.", ephemeral=True) 

    # Monthly Command
    @app_commands.command(name="monthly", description="Display your monthly study statistics")
    async def monthly(self, interaction: discord.Interaction):
        with open('ranking.json', 'r') as f:
            ranking_data = json.load(f)

        user_data = ranking_data.get(str(interaction.user.id))
        if not user_data:
            await interaction.response.send_message("You have no recorded stats.", ephemeral=True)
            return

        if 'total_time' not in user_data:
            await interaction.response.send_message("No monthly  time recorded for you.", ephemeral=True)
            return

        total_hours = user_data["total_time"]
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)

        embed = discord.Embed(
            title="Monthly Study Statistics <a:cutestar:1236936244722925609>",
            description=f"You have studied for {hours} hours and {minutes} minutes so far this month.",
            color=discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="Display your daily study statistics")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        ranking_file = 'ranking.json'
        
        # Load the ranking data from the JSON file
        if os.path.exists(ranking_file):
            with open(ranking_file, 'r') as f:
                ranking_data = json.load(f)
        else:
            await interaction.response.send_message("No ranking data found.", ephemeral=True)
            return

        # Fetch the user's data
        user_data = ranking_data.get(user_id)
        if not user_data:
            await interaction.response.send_message("You don't have any recorded study data.", ephemeral=True)
            return

        # Get the user's time zone
        user_time_zone = get_user_time_zone(user_id)
        current_date = datetime.now(user_time_zone).date()

        # Check if the last_reset is present
        last_reset = user_data.get('last_reset')
        if not last_reset:
            if user_data.get('daily_total_time', 0) > 0:
                user_data['last_reset'] = current_date.isoformat()
            else:
                user_data['last_reset'] = current_date.isoformat()
                user_data['daily_total_time'] = 0

            ranking_data[user_id] = user_data
            with open(ranking_file, 'w') as f:
                json.dump(ranking_data, f, indent=4)
        else:
            last_reset_date = datetime.fromisoformat(last_reset).date()
            if current_date > last_reset_date:
                user_data['daily_total_time'] = 0
                user_data['last_reset'] = current_date.isoformat()

                ranking_data[user_id] = user_data
                with open(ranking_file, 'w') as f:
                    json.dump(ranking_data, f, indent=4)
        
        daily_total_seconds = user_data.get('daily_total_time', 0) * 3600
        hours, remainder = divmod(daily_total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        embed = discord.Embed(
            title="Daily Study Statistics <a:cutestar:1236936244722925609>",
            description=f"You have studied for {int(hours)} hours and {int(minutes)} minutes so far today.",
            color=discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="profile", description="Shows your study profile, including ranks and study times")
    async def profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        ranking_file = 'ranking.json'

        # Load the ranking data from the JSON file
        if os.path.exists(ranking_file):
            with open(ranking_file, 'r') as f:
                ranking_data = json.load(f)
        else:
            await interaction.response.send_message("No ranking data found.", ephemeral=True)
            return

        # Fetch the user's data
        user_data = ranking_data.get(user_id)
        if not user_data:
            await interaction.response.send_message("You have no recorded stats.", ephemeral=True)
            return

        # Get the user's time zone
        user_time_zone = get_user_time_zone(user_id)
        current_date = datetime.now(user_time_zone).date()

        # Check if the last_reset is present
        last_reset = user_data.get('last_reset')
        if not last_reset:
            if user_data.get('daily_total_time', 0) > 0:
                user_data['last_reset'] = current_date.isoformat()
            else:
                user_data['last_reset'] = current_date.isoformat()
                user_data['daily_total_time'] = 0

            ranking_data[user_id] = user_data
            with open(ranking_file, 'w') as f:
                json.dump(ranking_data, f, indent=4)
        else:
            last_reset_date = datetime.fromisoformat(last_reset).date()
            if current_date > last_reset_date:
                user_data['daily_total_time'] = 0
                user_data['last_reset'] = current_date.isoformat()

                ranking_data[user_id] = user_data
                with open(ranking_file, 'w') as f:
                    json.dump(ranking_data, f, indent=4)

        total_hours = user_data["total_time"]
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)

        daily_total_seconds = user_data.get('daily_total_time', 0) * 3600
        daily_hours, daily_remainder = divmod(daily_total_seconds, 3600)
        daily_minutes, _ = divmod(daily_remainder, 60)

        voice_roles = [
            (1, 1230613685278474271),
            (3, 1230613683860934758),
            (6, 1230613682686529647),
            (10, 1230613680979181638),
            (20, 1230613679603716106),
            (40, 1230613677791772764),
            (80, 1230613676365713419),
            (120, 1234145726183899136),
            (160, 1234146333481369630),
            (200, 1234146649123590175),
        ]

        def get_role_by_hours(total_hours):
            for hours, role_id in reversed(voice_roles):
                if total_hours >= hours:
                    return role_id
            return None

        current_rank = get_role_by_hours(total_hours)
        next_rank_hours = next((hours for hours, role_id in voice_roles if hours > total_hours), None)
        next_role = next((role_id for hours, role_id in voice_roles if hours == next_rank_hours), None)
        next_rank_hours_needed = next_rank_hours - total_hours if next_rank_hours else None

        sorted_users = sorted(
            (user for user in ranking_data.items() if 'total_time' in user[1]),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        leaderboard_position = next(
            (i + 1 for i, (uid, data) in enumerate(sorted_users) if uid == str(interaction.user.id)),
            None
        )

        embed = discord.Embed(
            title="Study Profile <a:cutestar:1236936244722925609>",
            color = discord.Color(0x2B2D31)
        )
        embed.set_author(name=f"{interaction.user.name}'s Study Profile", icon_url=interaction.user.avatar.url)
        embed.add_field(name="Monthly Study Time", value=f"{hours} hours & {minutes} minutes", inline=False)
        embed.add_field(name="Daily Study Time", value=f"{int(daily_hours)} hours & {int(daily_minutes)} minutes", inline=False)
        embed.add_field(name="Current Rank", value=f"<@&{current_rank}>" if current_rank else "None", inline=False)
        embed.add_field(name="Next Rank", value=f"<@&{next_role}>" if next_role else "Max Rank Reached", inline=False)
        embed.add_field(name="Time Needed For Next Rank", value=f"{int(next_rank_hours_needed)} hours & {int((next_rank_hours_needed - int(next_rank_hours_needed)) * 60)} minutes" if next_rank_hours_needed else "N/A", inline=False)
        embed.add_field(name="Leaderboard Position", value=f"#{leaderboard_position}" if leaderboard_position else "N/A", inline=False)

        await interaction.response.send_message(embed=embed)



    @app_commands.command(name="leaderboard", description="Leaderboard of study statistics")
    async def leaderboard(self, interaction: discord.Interaction):
        ranking_file = 'ranking.json'

        # Check if the ranking.json file exists
        if not os.path.exists(ranking_file):
            await interaction.response.send_message("Ranking file not found.", ephemeral=True)
            return

        # Read the ranking data from the file
        with open(ranking_file, 'r') as f:
            ranking_data = json.load(f)

        # Sort users by total study time in descending order
        sorted_users = sorted(
            (user for user in ranking_data.items() if 'total_time' in user[1]),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )

        # Prepare the leaderboard embed
        embed = discord.Embed(
            title="Top 10 Study Enthusiasts In Girls Only",
            color = discord.Color(0x2B2D31)
        )
        embed.set_author(name="Study Leaderboard")

        # Add the top 10 users to the embed
        for i, (user_id, user_data) in enumerate(sorted_users[:10], start=1):
            user = await self.bot.fetch_user(int(user_id))
            total_hours = user_data["total_time"]
            hours = int(total_hours)
            minutes = int((total_hours - hours) * 60)
            embed.add_field(
                name=f"#{i}",
                value=f"{user.mention}: {hours} hours & {minutes} minutes",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(rank(bot))