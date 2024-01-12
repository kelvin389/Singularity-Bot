# Standard Library Imports
import os
import zoneinfo

# External Library Imports
from dotenv import load_dotenv

# Discord Imports
import discord
from discord import app_commands
from discord.ext import commands

# Custom Module Imports
from .modals.timezone_modal import TimezoneModal
from .objs.Event import Event
from .views.confirmation_buttons import ConfirmationButtons
from .views.timezone_buttons import TimezoneButtons
from .config import Config
from . import util

# dict {id: str(int): timezone: str}
# id must be a string because in JSON, all keys are strings
user_timezones = util.read_timezone_json()
print(user_timezones)

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix="!", intents=intents)

# this is a normal command, not a slash command.
# ie. typing '!sync' is the only way to activate this function,
# cant type /sync
@bot.command(name="sync")
async def sync(interaction: discord.Interaction):
    try:
        await bot.tree.sync()
        print("synced commands")
    except Exception as e:
        print("error syncing", e)
        exit(1)

@bot.tree.command(name="timezone", description="choose your timezone")
async def choose_timezone(interaction: discord.Interaction):
    # create the modal here because it needs access to user_timezones.
    # this also should slightly decreases the delay between pressing the input button and receiving the modal on the user end
    tz_modal = TimezoneModal(user_timezones)
    tz_buttons = TimezoneButtons(tz_modal)
    await interaction.response.send_message(content="epic infographic here (click link, copy timezone, come back to discord, click input, paste)", view=tz_buttons, ephemeral=True)

# request command for creating an event
@bot.tree.command(name="request", description="This command creates a event with participants")
@app_commands.describe(event="What's happening?")
@app_commands.describe(participants="Specify who you want to invite by mentioning them with @, similar to how you would ping them (eg. @kal @BenAstromo). Theres no need to include yourself.")
@app_commands.describe(time="What time of day the event is happening. Can use 12 or 24 hour time. (eg. 8:34 pm OR 20:34)")
@app_commands.describe(day="(Optional) Day of the month from 1-31. If left unspecified, the next possible time that your inputted time can occur is used. (eg. if its 11:59pm and you input 7:00pm, 7:00pm the next day will be assumed)")
@app_commands.describe(month="(Optional. Must also input day)")
@app_commands.describe(year="(Optional. Must also input day and month)")
@app_commands.choices(month=[
    app_commands.Choice(name="January", value=1),
    app_commands.Choice(name="February", value=2),
    app_commands.Choice(name="March", value=3),
    app_commands.Choice(name="April", value=4),
    app_commands.Choice(name="May", value=5),
    app_commands.Choice(name="June", value=6),
    app_commands.Choice(name="July", value=7),
    app_commands.Choice(name="August", value=8),
    app_commands.Choice(name="September", value=9),
    app_commands.Choice(name="October", value=10),
    app_commands.Choice(name="November", value=11),
    app_commands.Choice(name="December", value=12)])
async def make_request(interaction: discord.Interaction, event: str, participants: str, time: str, day: app_commands.Range[int, 1, 31]=None, month: int=None, year: int=None):
    if month and not day:
        await interaction.response.send_message("you set a month without day you donkey", ephemeral=True)
        return
    if year and (not day or not month):
        await interaction.response.send_message("you set a year without month or day you donkey", ephemeral=True)
        return

    host_tz = zoneinfo.ZoneInfo(user_timezones[str(interaction.user.id)])
    event_datetime = util.to_datetime(time, day, month, year, host_tz)
    event_timestamp = int(event_datetime.timestamp()) # event time in unix timestamp format

    absolute_time = ""
    if day:
        absolute_time = f"<t:{event_timestamp}:f>"
    else:
        absolute_time = f"<t:{event_timestamp}:t>"

    relative_time = f"<t:{event_timestamp}:R>"

    embed = discord.Embed()
    embed.title = f"{event} at {absolute_time} ({relative_time})"
    embed.colour = discord.Colour.blue()
    embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/original/001/708/596/db3.jpeg")
    embed.set_footer(text="!note [message] to leave a note (doesnt work lol)")

    participants = participants.strip() # list of participants each in format "<@[id]>"
    participants_lst = participants.split() # split with no args splits on all whitespace (multiple spaces, newlines, etc)
    inital_user_lst = util.participants_to_users(bot, interaction.user.id, participants_lst)
    event_obj = Event(event, inital_user_lst, embed)

    confirm_buttons = ConfirmationButtons(event_obj)
    await interaction.response.send_message("You are about to set up the following event. Is everything correct?", view=confirm_buttons, embed=embed, ephemeral=True)

# load token from .env and run bot
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
