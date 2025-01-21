import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import sqlite3
from datetime import datetime, timezone, timedelta
import os

# Other Imports
import json

# Get configuration.json
with open("configuration.json", "r") as config:
    data = json.load(config)
    token = data["token"]
    prefix = data["prefix"]

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
intents.guilds = True


bot = commands.Bot(prefix, intents = intents)

# Load cogs
initial_extensions = [
    "cogs.productivity",
    "cogs.ticketsystem",
    "cogs.moderation",
    "cogs.fun",
    "cogs.help",
    "cogs.colors",
    "cogs.room",
    "cogs.event",
    "cogs.tasks",
    "cogs.giveaway",
    "cogs.journal",
    "cogs.reminder",
    "cogs.ranking",
    "cogs.serverinfo"
]

async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {e}")
 
print(initial_extensions) 

@bot.command()
@commands.has_permissions(administrator=True)
async def syncthedamntree(ctx):
    await bot.tree.sync()
    await ctx.send("Command tree successfully synced. Keep the password a secret!")

@bot.command(name="reload", help="Reloads a specified cog.")
@commands.has_permissions(administrator=True)
async def reload(ctx, cog: str):
    try:
        await bot.reload_extension(cog)
        await ctx.send(f"Successfully reloaded `{cog}`.")
        print(f"Successfully reloaded `{cog}`.")
    except commands.ExtensionNotLoaded:
        await ctx.send(f"`{cog}` is not loaded.")
        print(f"`{cog}` is not loaded.")
    except commands.ExtensionNotFound:
        await ctx.send(f"Could not find the cog named `{cog}`.")
        print(f"Could not find the cog named `{cog}`.")
    except commands.NoEntryPointError:
        await ctx.send(f"The cog `{cog}` does not have a setup function.")
        print(f"The cog `{cog}` does not have a setup function.")
    except commands.ExtensionFailed as e:
        await ctx.send(f"Failed to reload `{cog}`.\n{type(e).__name__}: {e}")
        print(f"Failed to reload `{cog}`.\n{type(e).__name__}: {e}")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name ="/help"))
    print(discord.__version__)

def ensure_ranking_json():
    try:
        with open('ranking.json', 'r') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                # File is not valid JSON, initialize it
                ranking = {}
                with open('ranking.json', 'w') as wf:
                    json.dump(ranking, wf)
    except FileNotFoundError:
        # File does not exist, create it
        ranking = {}
        with open('ranking.json', 'w') as wf:
            json.dump(ranking, wf)
    return ranking

ranking_data = ensure_ranking_json()

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

rankup_channel_id = 1230613444827283516

# Function to convert GMT time zone string to a timezone object
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

def update_ranking_data(user_id, join_time=None, leave_time=None):
    ranking_file = 'ranking.json'
    
    # Load the ranking data from the JSON file
    if os.path.exists(ranking_file):
        with open(ranking_file, 'r') as f:
            ranking_data = json.load(f)
    else:
        ranking_data = {}

    user_data = ranking_data.get(user_id, {})
    
    # Fetch user time zone and current date according to that time zone
    user_time_zone = get_user_time_zone(user_id)
    current_date = datetime.now(user_time_zone).date()

    if 'last_reset' not in user_data:
        user_data['last_reset'] = current_date.isoformat()

    last_reset_date = datetime.fromisoformat(user_data['last_reset']).date()

    if current_date > last_reset_date:
        user_data['daily_total_time'] = 0  # Reset daily total time
        user_data['last_reset'] = current_date.isoformat()  # Update last reset date

    if join_time:
        # Save the join time in the ranking data
        user_data['last_join'] = join_time

    if leave_time:
        # Calculate the time spent in the voice channel
        last_join = user_data.get('last_join')
        if last_join:
            last_join = datetime.fromisoformat(last_join)  # Convert string to datetime
            leave_time = datetime.fromisoformat(leave_time)  # Convert string to datetime
            time_spent = (leave_time - last_join).total_seconds() / 3600  # Convert to hours
            total_time = user_data.get('total_time', 0) + time_spent
            daily_total_time = user_data.get('daily_total_time', 0) + time_spent
            user_data['total_time'] = total_time
            user_data['daily_total_time'] = daily_total_time
            del user_data['last_join']  # Remove last_join after calculating the time spent

    # Save updated user data back into ranking_data
    ranking_data[user_id] = user_data

    # Save the updated ranking data back to the JSON file
    with open(ranking_file, 'w') as f:
        json.dump(ranking_data, f, indent=4)

def get_role_by_hours(total_hours):
    for hours, role_id in reversed(voice_roles):
        if total_hours >= hours:
            return role_id
    return None

async def update_user_role(member):
    with open('ranking.json', 'r') as f:
        ranking_data = json.load(f)

    user_data = ranking_data.get(str(member.id))
    if not user_data:
        return

    total_hours = user_data["total_time"]
    new_role_id = get_role_by_hours(total_hours)
    if not new_role_id:
        return

    current_roles = [role.id for role in member.roles]
    new_role = discord.utils.get(member.guild.roles, id=new_role_id)

    if new_role_id not in current_roles:
        for hours, role_id in voice_roles:
            if role_id in current_roles:
                old_role = discord.utils.get(member.guild.roles, id=role_id)
                await member.remove_roles(old_role)
        
        await member.add_roles(new_role)

        embed = discord.Embed(
            title="<a:cutestar:1236936244722925609> Rank Up!",
            description=f"Congratulations, {member.mention}! You've ranked up! "
                        f"For working hard, you've earned the {new_role.mention} role. "
                        f"Keep up! :D",
            color = discord.Color(0x2B2D31)
        )
        embed.set_image(url="https://i.imgur.com/xIyAHeE.jpeg")

        channel = member.guild.get_channel(rankup_channel_id)
        await channel.send(f"{member.mention}", embed=embed)

import asyncio

async def check_camera_and_screenshare(member, after_channel, warning_channel, channel_ids_to_monitor):
    # Keep the passed channel IDs or define them here.
    channel_ids_to_monitor = [1234107232845561938, 1249024834571079811]
    await asyncio.sleep(120)

    # Check if the member is still in the monitored channel
    if not member.voice or member.voice.channel.id not in channel_ids_to_monitor:
        return

    voice_state = member.voice

    # If the user is in a monitored channel without camera or screenshare
    if voice_state.channel.id in channel_ids_to_monitor:
        if not voice_state.self_video and not voice_state.self_stream:
            await warning_channel.send(
                f"Hey there, {member.mention}! Please turn your camera on or screenshare, or you'll be disconnected from the channel within a minute!"
            )
        
        # Wait for another minute
        await asyncio.sleep(60)

        # Check again if the member is still in the monitored channel
        if not member.voice or member.voice.channel.id not in channel_ids_to_monitor:
            return

        voice_state = member.voice

        # If the user is still not sharing the camera or screen, disconnect them
        if not voice_state.self_video and not voice_state.self_stream:
            await member.move_to(None)


@bot.event
async def on_voice_state_update(member, before, after):
    category_id_to_monitor = 1236866824331595788
    channel_ids_to_monitor = [1234107232845561938, 1249024834571079811]
    warning_channel_id = 1230613444827283516
    room_data = load_room_data()

    def should_count_time(channel):
        if channel is None:
            return False
        if channel.category and channel.category.id == category_id_to_monitor:
            # Check if the channel is monitored
            channel_id_str = str(channel.id)
            if channel_id_str in room_data and room_data[channel_id_str].get("monitored") == "Yes":
                return True
            return False
        # If the channel is outside the monitored category, always count
        return True

    if before.channel is None and after.channel is not None:
        # User joined a voice channel
        if should_count_time(after.channel):
            update_ranking_data(str(member.id), join_time=datetime.now(timezone.utc).isoformat())

        if after.channel.id in channel_ids_to_monitor:
            warning_channel = bot.get_channel(warning_channel_id)
            asyncio.create_task(check_camera_and_screenshare(member, after.channel, warning_channel, channel_ids_to_monitor))

    elif before.channel is not None and after.channel is None:
        # User left a voice channel
        if should_count_time(before.channel):
            update_ranking_data(str(member.id), leave_time=datetime.now(timezone.utc).isoformat())
            await update_user_role(member)

    elif before.channel is not None and after.channel is not None:
        # User is still in a voice channel, check for changes in self_video or self_stream
        if (before.self_video and not after.self_video) or (before.self_stream and not after.self_stream):
            if after.channel.id in channel_ids_to_monitor:
                warning_channel = bot.get_channel(warning_channel_id)
                asyncio.create_task(check_camera_and_screenshare(member, after.channel, warning_channel, channel_ids_to_monitor))

class delete_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def this_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        user_id = None

        # Load the open tickets data
        try:
            with open('opentickets.json', 'r') as file:
                open_tickets = json.load(file)
        except FileNotFoundError:
            open_tickets = {}

        # Find the user ID corresponding to this channel
        for uid, cid in open_tickets.items():
            if cid == channel.id:
                user_id = uid
                break

        # Remove the user ID and channel ID from the open tickets data
        if user_id:
            del open_tickets[user_id]
            with open('opentickets.json', 'w') as file:
                json.dump(open_tickets, file, indent=4)

        embed = discord.Embed(
            title=f"Ticket will be deleted in 5 seconds.",
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

class verification_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.gray, emoji="📩")
    async def verification_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild
        user_id = str(interaction.user.id)
        
        # Ensure the opentickets.json file exists
        if not os.path.exists('opentickets.json'):
            with open('opentickets.json', 'w') as file:
                json.dump({}, file)

        # Load the open tickets data
        with open('opentickets.json', 'r') as file:
            open_tickets = json.load(file)

        # Check if the user already has an open ticket
        if user_id in open_tickets:
            open_ticket_channel_id = open_tickets[user_id]
            open_ticket_channel = guild.get_channel(open_ticket_channel_id)
            if open_ticket_channel:
                await interaction.response.send_message(
                    f"You already have an open ticket! Refer to: {open_ticket_channel.mention}",
                    ephemeral=True
                )
                return

        # If the user doesn't have an open ticket, create a new one
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(1233423130521768028): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        embed1 = discord.Embed(
            title=f"<a:cutestar:1236936244722925609> Verification Instructions",
            description="<:arrowpeach:1237691606778253443> Write your username along with today's date on a paper.\n<:arrowpeach:1237691606778253443> Take a selfie holding your personal ID & the paper, and cover any important information except your gender/sex, and date of birth.\n<:arrowpeach:1237691606778253443> Your face must be visible in the selfie.\n<:arrowpeach:1237691606778253443> Your hand must be visible holding your ID and the paper.\n<:arrowpeach:1237691606778253443> Send the selfie here.",
            color = discord.Color(0x2B2D31)
        )

        embed2 = discord.Embed(
            title=f"<a:cutestar:1236936244722925609> Frequently Asked Questions",
            description="<:arrowpeach:1237691606778253443> Can I send a voice message instead?\n- No.\n\n<:arrowpeach:1237691606778253443> Will my picture be shared anywhere?\n- No, the channel will automatically get deleted after you are verified.\n\n<:arrowpeach:1237691606778253443> My picture is mirrored due to my front camera.\n- That is okay. We discourage such edits made to images, go ahead and send it as it is.\n\n<:arrowpeach:1237691606778253443> Can I use my passport or driver's license instead?\n- As long as it states your Date of birth and sex/gender, yes. ",
            color = discord.Color(0x2B2D31)
        )

        embed3 = discord.Embed(
            title=f"<:arrowpeach:1237691606778253443> Feel free to ask any further questions here in this chat.\n\n<:arrowpeach:1237691606778253443> You will have full access to the server once verified.",
            color = discord.Color(0x2B2D31)
        )

        channel = await guild.create_text_channel(f"₊˚・{interaction.user.name}", overwrites=overwrites, category=guild.get_channel(1232270337711013940))

        # Add the new ticket to the open tickets data
        open_tickets[user_id] = channel.id
        with open('opentickets.json', 'w') as file:
            json.dump(open_tickets, file, indent=4)

        await interaction.response.send_message(f"Your verification ticket has been created. Refer to: {channel.mention}!", ephemeral=True)
        await channel.send(f"Welcome {interaction.user.mention}!\n<@&1233423130521768028>", embeds=[embed1, embed2, embed3], view=delete_button())

class close_help_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close_help_button(self, interaction: discord.Interaction, button: discord.ui.button):
        channel = interaction.channel
        embed = discord.Embed(
            title=f"Ticket will be deleted in 5 seconds.",
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

class help_support_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.gray, emoji="📩")
    async def help_support_button(self, interaction: discord.Interaction, button: discord.ui.button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(1233423130521768028): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        embed = discord.Embed(
            title="Welcome to Help & Support <a:cutestar:1236936244722925609>",
            description="Staff will be with you shortly. Please describe the issue in the meanwhile.",
            color = discord.Color(0x2B2D31)
        )

        channel = await guild.create_text_channel(f"₊˚・{interaction.user.name}", overwrites=overwrites, category=guild.get_channel(1233319936915669012))

        await interaction.response.send_message(f"Your Help & Support ticket has been created. Refer to: {channel.mention}!", ephemeral=True)
        await channel.send(f"Welcome {interaction.user.mention}!\n<@&1233423130521768028>", embed=embed, view=close_help_button())

def ensure_ranking_json():
    try:
        with open('ranking.json', 'r') as f:
            try:
                ranking = json.load(f)
            except json.JSONDecodeError:
                # File is not valid JSON, initialize it
                ranking = {}
                with open('ranking.json', 'w') as wf:
                    json.dump(ranking, wf)
    except FileNotFoundError:
        # File does not exist, create it
        ranking = {}
        with open('ranking.json', 'w') as wf:
            json.dump(ranking, wf)
    return ranking

# Call the function to ensure ranking.json is valid
ranking_data = ensure_ranking_json()


@bot.event
async def on_ready():
    channel_id = 1233320708642308139
    channel = bot.get_channel(channel_id)
    channel_id2 = 1241646289142157386
    channel2 = bot.get_channel(channel_id2)

    embed = discord.Embed(
        title="Help & Support <a:cutestar:1236936244722925609>",
        description="After reading the instructions, you can create a ticket by clicking the button below!",
        color = discord.Color(0x2B2D31)
    )
    
    embed2 = discord.Embed(
        title=f"Verification",
        description="<a:cutestar:1236936244722925609> Girls Only aims for a safe and inclusive space of just women of different backgrounds, beliefs and identities!\n\n<a:cutestar:1236936244722925609> We offer study calls and events that suit everyone's study preferences and paces!\n\n<a:cutestar:1236936244722925609> We require verification to make sure you are a girl/woman/female, as well as preventing trolling/DDOS attacks.\n\n<a:cutestar:1236936244722925609> IMPORTANT NOTE: WE ONLY TAKE AFABS IN. It's not that we're trying to discriminate a certain group, it's that we can never be too sure of someone's level of transition and we have to take this security measure as a precaution. (AFAB: Assigned Female At Birth)\n\n<a:cutestar:1236936244722925609> To create a verification ticket, click the 'Create Ticket' button below. You'll receive instructions on how to verify once you open a ticket.",
        color = discord.Color(0x2B2D31)
    )

    embed2.set_image(url="https://i.imgur.com/a8qYDmh.gif")

    await channel.send(embed=embed, view=help_support_button()) 
    await channel2.send(embed=embed2, view=verification_button())

LOCATION_ROLE_EMOJIS = {
    '⛰️': 1230599071610437703,
    '🏰': 1230599111456198746,
    '🦅': 1230599158767947907,
    '🌴': 1230599199721263154,
    '🐘': 1230599231299915886,
    '🌊': 1230599272555089961
}

EDUCATION_ROLE_EMOJIS = {
    '📚': 1230599400808517775,
    '📜': 1230599471981920286,
    '🖊️': 1230599533491126332,
    '🎓': 1230599571944505419
}

STUDY_ROLE_EMOJIS = {
    '1️⃣': 1232572641043415091,
    '2️⃣': 1232572771616428123,
    '📹': 1232583764165656628,
    '🌲': 1232584304328966175,
    '💻': 1234022170351501354,
    '📖': 1232584414895276083,
}

ANNOUNCEMENT_ROLE_EMOJIS = {
    '📣': 1232586559908216863,
    '🎉': 1232586714300813385,
    '👾': 1243408007468023829,
    '☀️': 1247426658189840384
}

# Define the message IDs to listen to
LOCATIONMESSAGEID = 1247428048312209523
EDUCATIONMESSAGEID = 1247428060257452032
STUDYMESSAGEID = 1247428067551350855
ANNOUNCEMENTSMESSAGEID = 1247428081195679785

rolechannel = 1247105321361604661

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id == LOCATIONMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in LOCATION_ROLE_EMOJIS:
            role_id = LOCATION_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).add_roles(role)

    elif payload.message_id == EDUCATIONMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in EDUCATION_ROLE_EMOJIS:
            role_id = EDUCATION_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).add_roles(role)

    elif payload.message_id == STUDYMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in STUDY_ROLE_EMOJIS:
            role_id = STUDY_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).add_roles(role)

    elif payload.message_id == ANNOUNCEMENTSMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in ANNOUNCEMENT_ROLE_EMOJIS:
            role_id = ANNOUNCEMENT_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == LOCATIONMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in LOCATION_ROLE_EMOJIS:
            role_id = LOCATION_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).remove_roles(role)

    elif payload.message_id == EDUCATIONMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in EDUCATION_ROLE_EMOJIS:
            role_id = EDUCATION_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).remove_roles(role)

    elif payload.message_id == STUDYMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in STUDY_ROLE_EMOJIS:
            role_id = STUDY_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).remove_roles(role)

    elif payload.message_id == ANNOUNCEMENTSMESSAGEID and payload.channel_id == rolechannel:
        emoji = payload.emoji.name if payload.emoji.id is None else str(payload.emoji.id)
        if emoji in ANNOUNCEMENT_ROLE_EMOJIS:
            role_id = ANNOUNCEMENT_ROLE_EMOJIS[emoji]
            guild = bot.get_guild(payload.guild_id)
            if guild:
                role = discord.utils.get(guild.roles, id=role_id)
                if role:
                    await guild.get_member(payload.user_id).remove_roles(role)

@bot.event
async def on_member_remove(member):
    # Log the leaving of the user
    channel_id = 1232348402470355086
    channel = bot.get_channel(channel_id)
    join_duration = datetime.now(timezone.utc) - member.joined_at
    days = join_duration.days
    hours, remainder = divmod(join_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    roles_mention = ' '.join([f"<@&{role.id}>" for role in member.roles if role.name != "@everyone"])
    embed = discord.Embed(title=f"{member.name} has left the server",
        description=f"They joined the server {days} days, {hours} hours, {minutes} minutes ago.",
        color=discord.Color.yellow())
    embed.add_field(name="Roles", value=roles_mention or "No roles", inline=False)
    embed.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar.url}")
    embed.set_footer(text=f"User ID: {member.id}")
    await channel.send(embed=embed)

    try:
        with open('opentickets.json', 'r') as file:
            open_tickets = json.load(file)
    except FileNotFoundError:
        open_tickets = {}

    user_id = str(member.id)

    # Check if the user has an open ticket
    if user_id in open_tickets:
        ticket_channel_id = open_tickets[user_id]
        ticket_channel = bot.get_channel(ticket_channel_id)
        
        if ticket_channel:
            # Send a message to the ticket channel
            leave_embed = discord.Embed(
                title="User has left the server.",
                description="The ticket will be deleted within 5 seconds.",
                color=discord.Color.red()
            )
            await ticket_channel.send(embed=leave_embed)

            # Remove the user ID and channel ID from the open tickets data
            del open_tickets[user_id]
            with open('opentickets.json', 'w') as file:
                json.dump(open_tickets, file, indent=4)

            # Wait for 5 seconds and then delete the ticket channel
            await asyncio.sleep(5)
            await ticket_channel.delete()

@bot.event
async def on_message_delete(message):
    channel_id = 1232348402470355086

    if message.author.bot:
        return
    
    channel = bot.get_channel(channel_id)
    deleted_message_channel = message.channel.mention
    deleted_message = message.content
    deleted_message_id = message.id

    embed = discord.Embed(
        title=f"Message deleted in {deleted_message_channel}",
        description=f"{deleted_message if deleted_message else 'No text content'}",
        color=discord.Color.red()
    )
    embed.set_author(name=f"{message.author.display_name}", icon_url=f"{message.author.avatar.url}")
    embed.set_footer(text=f"User ID: {message.author.id} • Message ID: {deleted_message_id}")

    await channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):
    channel_id = 1232348402470355086

    if before.author.bot:
        return
    
    channel = bot.get_channel(channel_id)

    # Information from the original (before edit) message
    original_message_channel = before.channel.mention
    original_message = before.content
    original_message_id = before.id

    # Information from the edited (after edit) message
    edited_message = after.content

    jump_link = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{original_message_id}"

    embed = discord.Embed(title=f"Message edited in {original_message_channel}",
        description=f"**Before:**\n{original_message}\n\n**After:**\n{edited_message}\n\n[Link]({jump_link})",
        color=discord.Color.orange())
    embed.set_author(name=f"{before.author.display_name}", icon_url=f"{before.author.avatar.url}")
    embed.set_footer(text=f"User ID: {before.author.id} • Message ID: {original_message_id}")
    await channel.send(embed=embed)

target_channel_id = 1232290868262867035
vent_channel_id = 1232344868093956226
last_bot_message_id = None
vent_last_bot_message_id = None

@bot.event
async def on_message(message):
    global last_bot_message_id
    global vent_last_bot_message_id

    # List of channel IDs to exclude from invite deletion
    excluded_channels = [1247887099294781612, 1230616238787395715, 1264518200469753867]

    # Check for Discord server invites and handle them, excluding specified channels and ignoring bot messages
    if not message.author.bot and ("discord.gg/" in message.content or "discord.com/invite/" in message.content) and message.channel.id not in excluded_channels:
        # Delete the message containing the invite
        await message.delete()

        # Send a notification to the specified channel with the role pinged
        notification_channel = bot.get_channel(1230615494327795904)
        await notification_channel.send(
            f"{message.author.mention} has sent a Discord server invite in {message.channel.mention}. "
            "The message was deleted. Here is the deleted message: "
            f"{message.content}"
        )

    # Create a thread for suggestions in the specific channel
    if message.channel.id == 1232282212788080690:
        thread = await message.channel.create_thread(
            name=message.content[:50],  # Use the first 50 characters of the message as the thread name
            message=message
        )
        await thread.send(f"Thanks for your suggestion, {message.author.mention}! Staff will be with you as soon as they join this thread.")

    # Send the message template in the specified channel and delete the previous bot message
    if message.channel.id == target_channel_id and not message.author.bot:
        # Delete the previous bot message if it exists
        if last_bot_message_id:
            try:
                previous_message = await message.channel.fetch_message(last_bot_message_id)
                await previous_message.delete()
            except discord.NotFound:
                pass

        # Send the new message
        bot_message = await message.channel.send(
            "﹒Name: \n"
            "﹒Age: \n"
            "﹒Country: \n"
            "﹒Time Zone (In GMT): \n"
            "﹒Education and Major: \n"
            "﹒Are You Looking For a Study-buddy? (Yes/No): \n"
            "﹒Interests: \n"
            "﹒Two Fun Facts: \n"
            "﹒Socials (Optional): \n"
            "﹒Anything To Add (Optional):"
        )

        # Store the bot message ID
        last_bot_message_id = bot_message.id

    await bot.process_commands(message)

    # Send the message template in the specified channel and delete the previous bot message
    if message.channel.id == vent_channel_id and not message.author.bot:
        # Delete the previous bot message if it exists
        if vent_last_bot_message_id:
            try:
                previous_message = await message.channel.fetch_message(vent_last_bot_message_id)
                await previous_message.delete()
            except discord.NotFound:
                pass

        # Send the new message
        bot_message = await message.channel.send(
            "`Use light signal whenever you vent to tell us how to react`\n\n"
            "🟩 = say whatever idgaf\n"
            "🟧 = you can reply but please be considerate\n"
            "🟥 = do not reply\n\n"
            "`If you do refuse to use light signal, we are not responsible for any misunderstandings.`"
        )

        # Store the bot message ID
        vent_last_bot_message_id = bot_message.id

    await bot.process_commands(message)

asyncio.run(load_extensions())
bot.run(token)