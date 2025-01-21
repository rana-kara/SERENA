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

COLOR_ROLES = {
    "Color 1": 1233353193354690632,
    "Color 2": 1233353301249101964,
    "Color 3": 1233353391250608148,
    "Color 4": 1233353504689618964,
    "Color 5": 1233353910098333768,
    "Color 6": 1233354006106079243,
    "Color 7": 1233354109508386876,
    "Color 8": 1233354208812732478,
    "Color 9": 1233354328996188180,
    "Color 10": 1233354532897947720,
    "Color 11": 1233354639324483666,
    "Color 12": 1233354736141598763,
    "Color 13": 1233354886121521223,
    "Color 14": 1233355014517428345,
    "Color 15": 1233355098198114356,
    "Color 16": 1233355240183693312,
    "Color 17": 1233355415341760523,
    "Color 18": 1233355492814880879,
    "Color 19": 1233355587438514218,
    "Color 20": 1233355678257643571,
    "Color 21": 1233355805240197150,
    "Color 22": 1233355920440954901,
    "Color 23": 1233356019569262612,
    "Color 24": 1233356088813027368,
    "Chromatic 1": 1236561018348372039,
    "Chromatic 2": 1236561108492615752,
    "Chromatic 3": 1236561191414005781,
    "Chromatic 4": 1236561280127729734,
    "Chromatic 5": 1236561376932003950,
    "Chromatic 6": 1236561464261742593,
    "Chromatic 7": 1236561557782134846,
    "Chromatic 8": 1236561642645618730,
    "Chromatic 9": 1236561756650737734,
    "Chromatic 10": 1236561843657637949,
    "Chromatic 11": 1236561943691661345,
    "Chromatic 12": 1236562017708675102,
    "Chromatic 13": 1236562087015092278,
    "Chromatic 14": 1236562176681185280
}

class colorselectpastel(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Color 1"),
            discord.SelectOption(label="Color 2"),
            discord.SelectOption(label="Color 3"),
            discord.SelectOption(label="Color 4"),
            discord.SelectOption(label="Color 5"),
            discord.SelectOption(label="Color 6"),
            discord.SelectOption(label="Color 7"),
            discord.SelectOption(label="Color 8"),
            discord.SelectOption(label="Color 9"),
            discord.SelectOption(label="Color 10"),
            discord.SelectOption(label="Color 11"),
            discord.SelectOption(label="Color 12"),
            discord.SelectOption(label="Color 13"),
            discord.SelectOption(label="Color 14"),
            discord.SelectOption(label="Color 15"),
            discord.SelectOption(label="Color 16"),
            discord.SelectOption(label="Color 17"),
            discord.SelectOption(label="Color 18"),
            discord.SelectOption(label="Color 19"),
            discord.SelectOption(label="Color 20"),
            discord.SelectOption(label="Color 21"),
            discord.SelectOption(label="Color 22"),
            discord.SelectOption(label="Color 23"),
            discord.SelectOption(label="Color 24")
            ]
        super().__init__(placeholder="Select a pastel color role!",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        # Get the selected role ID
        selected_role_id = COLOR_ROLES[self.values[0]]
        selected_role = guild.get_role(selected_role_id)

        # Remove any existing color roles
        roles_to_remove = [role for role in user.roles if role.id in COLOR_ROLES.values()]
        for role in roles_to_remove:
            await user.remove_roles(role)

        # Add the new color role
        await user.add_roles(selected_role)

        # Send a response
        await interaction.response.send_message(content="You got your role! Your previous role has been removed.", ephemeral=True)

class colorselectchromatic(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="Chromatic 1"),
            discord.SelectOption(label="Chromatic 2"),
            discord.SelectOption(label="Chromatic 3"),
            discord.SelectOption(label="Chromatic 4"),
            discord.SelectOption(label="Chromatic 5"),
            discord.SelectOption(label="Chromatic 6"),
            discord.SelectOption(label="Chromatic 7"),
            discord.SelectOption(label="Chromatic 8"),
            discord.SelectOption(label="Chromatic 9"),
            discord.SelectOption(label="Chromatic 10"),
            discord.SelectOption(label="Chromatic 11"),
            discord.SelectOption(label="Chromatic 12"),
            discord.SelectOption(label="Chromatic 13"),
            discord.SelectOption(label="Chromatic 14")
            ]
        super().__init__(placeholder="Select a chromatic color role!",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        # Get the selected role ID
        selected_role_id = COLOR_ROLES[self.values[0]]
        selected_role = guild.get_role(selected_role_id)

        # Remove any existing color roles
        roles_to_remove = [role for role in user.roles if role.id in COLOR_ROLES.values()]
        for role in roles_to_remove:
            await user.remove_roles(role)

        # Add the new color role
        await user.add_roles(selected_role)

        # Send a response
        await interaction.response.send_message(content="You got your role! Your previous role has been removed.", ephemeral=True)

class ColorViewPastel(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(colorselectpastel())

class ColorViewChromatic(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(colorselectchromatic())

class Colors(commands.GroupCog, name="colors", description="Pick colors"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    @app_commands.command(name="pastel", description="Pick a pastel color")
    async def pastel(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Here's how the colors look! Select one using the menu below.",
            description="<@&1233353193354690632>\n<@&1233353301249101964>\n<@&1233353391250608148>\n<@&1233353504689618964>\n<@&1233353910098333768>\n<@&1233354006106079243>\n<@&1233354109508386876>\n<@&1233354208812732478>\n<@&1233354328996188180>\n<@&1233354532897947720>\n<@&1233354639324483666>\n<@&1233354736141598763>\n<@&1233354886121521223>\n<@&1233355014517428345>\n<@&1233355098198114356>\n<@&1233355240183693312>\n<@&1233355415341760523>\n<@&1233355492814880879>\n<@&1233355587438514218>\n<@&1233355678257643571>\n<@&1233355805240197150>\n<@&1233355920440954901>\n<@&1233356019569262612>\n<@&1233356088813027368>",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed, view=ColorViewPastel(), ephemeral=True)

    @app_commands.command(name="chromatic", description="Pick a chromatic color")
    async def chromatic(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Here's how the colors look! Select one using the menu below.",
            description="<@&1236561018348372039>\n<@&1236561108492615752>\n<@&1236561191414005781>\n<@&1236561280127729734>\n<@&1236561376932003950>\n<@&1236561464261742593>\n<@&1236561557782134846>\n<@&1236561642645618730>\n<@&1236561756650737734>\n<@&1236561843657637949>\n<@&1236561943691661345>\n<@&1236562017708675102>\n<@&1236562087015092278>\n<@&1236562176681185280>",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed, view=ColorViewChromatic(), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Colors(bot))