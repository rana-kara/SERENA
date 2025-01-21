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

with open("configuration.json", "r") as config:
    data = json.load(config)
    token = data["token"]
    prefix = data["prefix"]

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(prefix, intents = intents)
class reminder(commands.GroupCog, name="reminder", description="Reminder commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="remindme", description="Sets a reminder, pings you when your reminder is done.")
    async def remindme(self, interaction: discord.Interaction, message: str, time: str) -> None:
        try:
            # Parse the reminder time and check if it is in the future
            reminder_time = datetime.strptime(time, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if reminder_time <= now:
                await interaction.response.send_message("The reminder time must be in the future.", ephemeral=True)
                return

            # Schedule the reminder in the bot's scheduler
            self.bot.scheduler.schedule_event(
                dispatch_name="reminder",
                dispatch_guild=interaction.guild.id,
                dispatch_user=interaction.user.id,
                dispatch_time=reminder_time.strftime("%Y-%m-%d %H:%M"),
                dispatch_zone="utc",
                dispatch_extra=dict(channel_id=interaction.channel.id, msg=message),
            )

            # Save the reminder to the database
            conn = sqlite3.connect("reminders.db")
            c = conn.cursor()
            c.execute("INSERT INTO reminders (user_id, reminder_time, message) VALUES (?, ?, ?)",
                      (interaction.user.id, reminder_time.isoformat(), message))
            conn.commit()
            conn.close()

            await interaction.response.send_message(f"Reminder set for {reminder_time}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to set the reminder.", ephemeral=True)
            print(e)

    @app_commands.command(name="cancel", description="Cancels one of your existing reminders.")
    async def cancel(self, interaction: discord.Interaction, reminder_id: int) -> None:
        try:
            # Delete the reminder from the database
            conn = sqlite3.connect("reminders.db")
            c = conn.cursor()
            c.execute("DELETE FROM reminders WHERE reminder_id = ? AND user_id = ?", (reminder_id, interaction.user.id))
            conn.commit()
            conn.close()
            await interaction.response.send_message(f"Cancelled reminder with ID {reminder_id}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to cancel the reminder.", ephemeral=True)
            print(e)

    @app_commands.command(name="clear", description="Clears ALL of your reminders.")
    async def clear(self, interaction: discord.Interaction) -> None:
        try:
            # Delete all reminders for the user from the database
            conn = sqlite3.connect("reminders.db")
            c = conn.cursor()
            c.execute("DELETE FROM reminders WHERE user_id = ?", (interaction.user.id,))
            conn.commit()
            conn.close()
            await interaction.response.send_message("Cleared all your reminders.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to clear the reminders.", ephemeral=True)
            print(e)

    @app_commands.command(name="list", description="Lists all of your existing reminders.")
    async def list(self, interaction: discord.Interaction) -> None:
        try:
            # Retrieve all reminders for the user from the database
            conn = sqlite3.connect("reminders.db")
            c = conn.cursor()
            c.execute("SELECT reminder_id, reminder_time, message FROM reminders WHERE user_id = ?", (interaction.user.id,))
            reminders = c.fetchall()
            conn.close()

            # Create an embed to display the reminders
            if reminders:
                embed = discord.Embed(
                    title="Your Reminders",
                    description="\n".join([f"ID: {r[0]}, Time: {r[1]}, Message: {r[2]}" for r in reminders]),
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="Your Reminders",
                    description="You have no reminders.",
                    color=discord.Color.red()
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Failed to list the reminders.", ephemeral=True)
            print(e)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(reminder(bot))

# Add the scheduler implementation
class Scheduler:
    def __init__(self, bot):
        self.bot = bot
        self.events = []
        self.check_events.start()

    def schedule_event(self, dispatch_name, dispatch_guild, dispatch_user, dispatch_time, dispatch_zone, dispatch_extra):
        # Schedule an event to be triggered at the specified time
        event_time = datetime.strptime(dispatch_time, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        self.events.append({
            'name': dispatch_name,
            'guild_id': dispatch_guild,
            'user_id': dispatch_user,
            'time': event_time,
            'zone': dispatch_zone,
            'extra': dispatch_extra
        })

    @tasks.loop(minutes=1)
    async def check_events(self):
        # Check scheduled events every minute
        now = datetime.now(timezone.utc)
        for event in self.events:
            if event['time'] <= now:
                user = self.bot.get_user(event['user_id'])
                channel = self.bot.get_channel(event['extra']['channel_id'])
                if user and channel:
                    await channel.send(f"{user.mention}, this is your reminder: {event['extra']['msg']}")
                self.events.remove(event)
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(reminder(bot))