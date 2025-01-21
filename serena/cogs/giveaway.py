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
import random

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

def load_giveaway_data():
    try:
        with open("giveaway.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    
# Helper function to save giveaway data
def save_giveaway_data(data):
    with open("giveaway.json", "w") as file:
        json.dump(data, file, indent=4)

# Helper function to convert duration string to relative Discord timestamp
def parse_duration(duration_str):
    if duration_str.endswith("h") and duration_str[:-1].isdigit():
        hours = int(duration_str[:-1])
        end_time = datetime.now(timezone.utc) + timedelta(hours=hours)
        # Get Unix timestamp and convert to int
        timestamp = int(end_time.timestamp())
        # Format end time as Discord timestamp
        return f"<t:{timestamp}:R>"
    else:
        raise ValueError("Invalid duration format. Please use the format Xh for specifying hours.")

class giveaway(commands.GroupCog, name="giveaway", description="Giveaway commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 
        self.giveaway_counter = 0

    @app_commands.command(name="create", description="Create a giveaway")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def create(self, interaction: discord.Interaction, prize: str, winners: int, channel: discord.TextChannel, duration: str) -> None:
        self.giveaway_counter += 1
        giveaway_id = self.giveaway_counter
        giveaway_data = load_giveaway_data()

        # Send giveaway message
        embed2 = discord.Embed(
            title=f"{prize} Giveaway! <a:cutestar:1236936244722925609>",
            description=f"Number Of Winners: {winners}\n\nClick the *enter giveaway* button below to enter the giveaway!\n\nGiveaway ends in {parse_duration(duration)}",
            color = discord.Color(0x2B2D31)
        )
        embed2.set_footer(text=f"Giveaway ID: {giveaway_id}")
        embed2.set_image(url="https://cdn.discordapp.com/attachments/1230615494327795904/1246831398875172875/giveawaybanner.gif?ex=665dd1ba&is=665c803a&hm=ebff671982d2a405ced2e084f561365c6707d5711fdb6ddb71a72a564cc48c7b&")

        class EnterGiveaway(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.green)
            async def enter_button(self, interaction: discord.Interaction, button: discord.ui.button):
                user_id = str(interaction.user.id)
                giveaway_data = load_giveaway_data()

                
                # Find the giveaway based on the message link
                for data in giveaway_data.values():
                    if data["message_link"] == interaction.message.jump_url:
                        if user_id in data["participants"]:
                            await interaction.response.send_message("You can't enter a giveaway twice.", ephemeral=True)
                        else:
                            # Add the user to the participants list
                            data["participants"].append(user_id)
                            save_giveaway_data(giveaway_data)
                            await interaction.response.send_message("You have successfully entered the giveaway.", ephemeral=True)
                        break

        giveaway_message = await channel.send(embed=embed2, view=EnterGiveaway())
        message_link = giveaway_message.jump_url  # Get the message link

        giveaway_data[giveaway_id] = {
            "prize": prize,
            "winners": winners,
            "channel_id": channel.id,
            "end_time": parse_duration(duration),
            "participants": [],
            "winners_selected": False,
            "message_link": message_link  # Store the message link
        }

        save_giveaway_data(giveaway_data)

        # Respond to the user
        await interaction.response.send_message("Giveaway successfully created.", ephemeral=False) 

    @app_commands.command(name="reroll", description="Reroll a giveaway")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def reroll(self, interaction: discord.Interaction, id: int) -> None:
        giveaway_data = load_giveaway_data()
        
        if str(id) not in giveaway_data:
            await interaction.response.send_message("Invalid giveaway ID.", ephemeral=True)
            return
        
        if giveaway_data[str(id)]["winners_selected"]:
            participants = giveaway_data[str(id)]["participants"]
            new_winner = random.choice(participants)
            channel_id = giveaway_data[str(id)]["channel_id"]
            channel = self.bot.get_channel(channel_id)
            prize = giveaway_data[str(id)]["prize"]
            
            # Notify the new winner
            new_winner_user = await self.bot.fetch_user(int(new_winner))
            await channel.send(f"{new_winner_user.mention} has won the reroll of the {prize} giveaway!")
            await interaction.response.send_message("Giveaway rerolled!")
            
        else:
            await interaction.response.send_message("This giveaway hasn't ended yet.", ephemeral=True)


    @app_commands.command(name="list", description="A list of currently active giveaways")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def list(self, interaction: discord.Interaction) -> None:
        giveaway_data = load_giveaway_data()
        
        active_giveaways = [(giveaway_id, data["prize"]) for giveaway_id, data in giveaway_data.items() if not data["winners_selected"]]
        
        if not active_giveaways:
            await interaction.response.send_message("There are no active giveaways at the moment.")
            return
        
        embed = discord.Embed(
            title="<a:cutestar:1236936244722925609> Active Giveaways <a:cutestar:1236936244722925609>",
            description="Here are the currently active giveaways:",
            color = discord.Color(0x2B2D31)
        )
        
        for giveaway_id, prize in active_giveaways:
            embed.add_field(name=f"Prize: {prize}", value=f"Giveaway ID: {giveaway_id}\n\u200b", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="end", description="End a giveaway")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def end(self, interaction: discord.Interaction, id: int) -> None:
        giveaway_data = load_giveaway_data()
        
        if str(id) not in giveaway_data:
            await interaction.response.send_message("Invalid giveaway ID.", ephemeral=True)
            return
        
        if giveaway_data[str(id)]["winners_selected"]:
            await interaction.response.send_message("This giveaway has already ended.", ephemeral=True)
            return
        
        participants = giveaway_data[str(id)]["participants"]
        winners_count = giveaway_data[str(id)]["winners"]
        channel_id = giveaway_data[str(id)]["channel_id"]
        prize = giveaway_data[str(id)]["prize"]
        message_link = giveaway_data[str(id)]["message_link"]
        
        if not participants:
            await interaction.response.send_message("No participants entered this giveaway.", ephemeral=True)
            return
        
        winners = random.sample(participants, min(winners_count, len(participants)))
        channel = self.bot.get_channel(channel_id)
        
        embed = discord.Embed(
            title=f"Giveaway For {prize} Ended! <a:cutestar:1236936244722925609>",
            description=f"Winners: {', '.join([f'<@{winner}>' for winner in winners])}",
            color = discord.Color(0x2B2D31)
        )
        
        await channel.send(embed=embed)
        
        giveaway_data[str(id)]["winners_selected"] = True
        save_giveaway_data(giveaway_data)
        
        await interaction.response.send_message("The giveaway has ended and winners have been announced.", ephemeral=False)

        message_id = int(message_link.split('/')[-1])
        giveaway_message = await channel.fetch_message(message_id)

        new_embed = giveaway_message.embeds[0]
        new_embed.title = f"{prize} Giveaway Ended!"
        new_embed.description = f"Winners: {', '.join([f'<@{winner}>' for winner in winners])}"
        new_view = discord.ui.View()  # Create an empty view to remove the button
        await giveaway_message.edit(embed=new_embed, view=new_view)

    @app_commands.command(name="info", description="See information about a giveaway")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def info(self, interaction: discord.Interaction, id: int) -> None:
        giveaway_data = load_giveaway_data()
        
        if str(id) not in giveaway_data:
            await interaction.response.send_message("Invalid giveaway ID.", ephemeral=True)
            return
        
        data = giveaway_data[str(id)]
        
        embed = discord.Embed(
            title=f"Giveaway Information (ID: {id}) <a:cutestar:1236936244722925609>",
            color = discord.Color(0x2B2D31)
        )
        embed.add_field(name="Prize", value=data["prize"], inline=False)
        embed.add_field(name="Winners", value=data["winners"], inline=False)
        embed.add_field(name="End Time", value=data["end_time"], inline=False)
        embed.add_field(name="Participants", value=len(data["participants"]), inline=False)
        embed.add_field(name="Winners Selected", value="Yes" if data["winners_selected"] else "No", inline=False)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="participants", description="See participants of a giveaway")
    @app_commands.checks.has_any_role(1233423130521768028)
    async def participants(self, interaction: discord.Interaction, id: int) -> None:
        giveaway_data = load_giveaway_data()

        if str(id) not in giveaway_data:
            await interaction.response.send_message("Invalid giveaway ID.", ephemeral=True)
            return

        participants = giveaway_data[str(id)]["participants"]

        embed = discord.Embed(
            title=f"Participants of Giveaway (ID: {id}) <a:cutestar:1236936244722925609>",
            description="\n".join([f"<@{participant}>" for participant in participants]),
            color = discord.Color(0x2B2D31)
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(giveaway(bot))