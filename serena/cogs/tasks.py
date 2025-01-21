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

class tasks(commands.GroupCog, name="tasks", description="Task-related commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__() 

    def load_tasks(self):
        if not os.path.exists("tasks.json"):
            return {}
        with open("tasks.json", "r") as file:
            return json.load(file)

    def save_tasks(self, tasks):
        with open("tasks.json", "w") as file:
            json.dump(tasks, file, indent=4)

    @app_commands.command(name="add", description="Add a task to your task list")
    async def add(self, interaction: discord.Interaction, task: str) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id not in tasks:
            tasks[user_id] = []

        tasks[user_id].append(task)
        self.save_tasks(tasks)

        embed = discord.Embed(
            description=f"**Task:** {task}",
            color = discord.Color(0x2B2D31)
        )
        embed.set_author(name=f"You added a task!")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="list", description="See your task list")
    async def list(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id in tasks and tasks[user_id]:
            description = "\n".join(f"- {task}" for task in tasks[user_id])
        else:
            description = "You haven't added any tasks yet."

        embed = discord.Embed(
            description=description,
            color = discord.Color(0x2B2D31)
        )
        embed.set_author(name=f"{interaction.user.display_name}'s Task List", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Clear your task list")
    async def clear(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id in tasks:
            del tasks[user_id]
            self.save_tasks(tasks)

        embed = discord.Embed(
            description="Your task list has been cleared.",
            color = discord.Color(0x2B2D31)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="remove", description="Remove a task from your task list")
    async def remove(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id in tasks:
            class taskremoveselect(discord.ui.Select):
                def __init__(self):
                    options = [discord.SelectOption(label=task, value=task) for task in tasks[user_id]]
                    super().__init__(placeholder="Select a task to remove!",max_values=1,min_values=1,options=options)

                def load_tasks(self):
                    if not os.path.exists("tasks.json"):
                        return {}
                    with open("tasks.json", "r") as file:
                        return json.load(file)

                def save_tasks(self, tasks):
                    with open("tasks.json", "w") as file:
                        json.dump(tasks, file, indent=4)

                async def callback(self, interaction: discord.Interaction):
                    selected_task = self.values[0]
                    tasks[user_id].remove(selected_task)
                    self.save_tasks(tasks)

                    embed = discord.Embed(
                        description=f"The task **{selected_task}** has been removed from your task list.",
                        color = discord.Color(0x2B2D31)
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            class taskremoveview(discord.ui.View):
                def __init__(self, *, timeout=180):
                    super().__init__(timeout=timeout)
                    self.add_item(taskremoveselect())

            embed = discord.Embed(
                title= "Select a task to remove!",
                description = "\n".join(f"- {task}" for task in tasks[user_id]),
                color = discord.Color(0x2B2D31)
            )
            embed.set_author(name=f"{interaction.user.display_name}'s Task List", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, view=taskremoveview(), ephemeral=True)

        else:
            embed = discord.Embed(
                description="You don't have any tasks to remove.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="check", description="Check a task in your task list")
    async def check(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id in tasks:
            class checktaskselect(discord.ui.Select):
                def __init__(self):
                    options = [discord.SelectOption(label=task, value=task) for task in tasks[user_id]]
                    super().__init__(placeholder="Select a task to check!",max_values=1,min_values=1,options=options)

                def load_tasks(self):
                    if not os.path.exists("tasks.json"):
                        return {}
                    with open("tasks.json", "r") as file:
                        return json.load(file)

                def save_tasks(self, tasks):
                    with open("tasks.json", "w") as file:
                        json.dump(tasks, file, indent=4)

                async def callback(self, interaction: discord.Interaction):
                    selected_task = self.values[0]
                    modified_task = f"~~{selected_task.strip()}~~"
                    tasks[user_id][tasks[user_id].index(selected_task)] = modified_task
                    self.save_tasks(tasks)

                    embed = discord.Embed(
                        description=f"The task **{selected_task}** has been checked.",
                        color = discord.Color(0x2B2D31)
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            class checktaskview(discord.ui.View):
                def __init__(self, *, timeout=180):
                    super().__init__(timeout=timeout)
                    self.add_item(checktaskselect())

            embed = discord.Embed(
                title= "Select a task to check!",
                description = "\n".join(f"- {task}" for task in tasks[user_id]),
                color = discord.Color(0x2B2D31)
            )
            embed.set_author(name=f"{interaction.user.display_name}'s Task List", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, view=checktaskview(), ephemeral=True)

        else:
            embed = discord.Embed(
                description="You don't have any tasks to check.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="uncheck", description="Uncheck a task in your task list")
    async def uncheck(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        tasks = self.load_tasks()

        if user_id in tasks:
            class unchecktaskselect(discord.ui.Select):
                def __init__(self):
                    options = [discord.SelectOption(label=task, value=task) for task in tasks[user_id]]
                    super().__init__(placeholder="Select a task to uncheck!",max_values=1,min_values=1,options=options)

                def load_tasks(self):
                    if not os.path.exists("tasks.json"):
                        return {}
                    with open("tasks.json", "r") as file:
                        return json.load(file)

                def save_tasks(self, tasks):
                    with open("tasks.json", "w") as file:
                        json.dump(tasks, file, indent=4)

                async def callback(self, interaction: discord.Interaction):
                    selected_task = self.values[0]
                    modified_task = selected_task.strip().replace("~~", "")
                    tasks[user_id][tasks[user_id].index(selected_task)] = modified_task  # Modify task status
                    self.save_tasks(tasks)

                    embed = discord.Embed(
                        description=f"The task **{modified_task}** has been unchecked.",
                        color = discord.Color(0x2B2D31)
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)

            class unchecktaskview(discord.ui.View):
                def __init__(self, *, timeout=180):
                    super().__init__(timeout=timeout)
                    self.add_item(unchecktaskselect())

            embed = discord.Embed(
                title= "Select a task to uncheck!",
                description = "\n".join(f"- {task}" for task in tasks[user_id]),
                color = discord.Color(0x2B2D31)
            )
            embed.set_author(name=f"{interaction.user.display_name}'s Task List", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, view=unchecktaskview(), ephemeral=True)

        else:
            embed = discord.Embed(
                description="You don't have any tasks to uncheck.",
                color = discord.Color(0x2B2D31)
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tasks(bot))
    