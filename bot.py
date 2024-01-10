# Standard Library Imports
import os
import re
import datetime
import json
import zoneinfo

# External Library Imports
from dateutil import relativedelta
from dotenv import load_dotenv

# Discord Imports
import discord
from discord import app_commands
from discord.ext import commands

# Custom Module Imports
import User
import Event
from views.confirmation_buttons import ConfirmationButtons
from views.timezone_buttons import TimezoneButtons

TIMEZONE_JSON_DIR = "user_timezones.json"

# dict {id: str(int): timezone: str}
# id must be a string because in JSON, all keys are strings
user_timezones = {}

with open(TIMEZONE_JSON_DIR, "r") as f:
    try:
        user_timezones = json.load(f)
        print(user_timezones)
    except:
        # if file doesnt exist or is empty
        None

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
    tz_buttons = TimezoneButtons()
    await interaction.response.send_message(content="epic infographic here", view=tz_buttons, ephemeral=True)

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
    event_datetime = to_datetime(time, day, month, year, host_tz)
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
    inital_user_lst = participants_to_users(interaction.user.id, participants_lst)
    event_obj = Event.Event(event, inital_user_lst, embed)

    confirm_buttons = ConfirmationButtons(event_obj)
    await interaction.response.send_message("You are about to set up the following event. Is everything correct?", view=confirm_buttons, embed=embed, ephemeral=True)

# convert host and list of participants to a list of users.
# host is int, participants list is list of strings: ["<@[id1]>", "<@[id2]>", ...]
def participants_to_users(host_id, participants_lst): 
    user_lst = []   

    disc_usr = bot.get_user(host_id)
    host_u = User.User(host_id, disc_usr, User.STATUS_HOST)
    user_lst.append(host_u)
    # turn participants into User objects and append them to user list
    for p_str in participants_lst:
        # NOTE: this results in the id being extracted from the string only to be added back inside of the User constructor.
        # bad efficiency but done for the sake for readability
        match = re.search(r"<@(\d+)>", p_str)
        id = int(match.group(1))
        disc_usr = bot.get_user(id)

        u = User.User(id, disc_usr, User.STATUS_UNDECIDED)
        user_lst.append(u)
    
    return user_lst

def to_datetime(time: str, input_day: int, input_month: int, input_year: int, timezone: zoneinfo.ZoneInfo):
    now = datetime.datetime.now().astimezone() # astimezone() defaults to the local timezone

    day = input_day if input_day else now.day
    month = input_month if input_month else now.month
    year = input_year if input_year else now.year
    
    # regex magic to extract the 1 (+2 optional) components from time string (11:59pm -> pulls out 11, 59, pm)
    # if minutes is missing, 0 is assumed. if period is missing, 24 hour format is assumed
    match = re.match(r"^(\d{1,2})(?::(\d{2}))?\s?([apAP][mM])?$", time)
    hr = int(match.group(1))
    min = int(match.group(2)) if match.group(2) else 0
    period = match.group(3).lower() if match.group(3) else None

    # convert 12 hour to 24 hour time
    # period will be discarded if a 24hr time is inputted with period (eg. 15:00am will be taken as 15:00 = 3:00pm)
    if (hr < 12 and period == "pm"):
        hr += 12
    elif hr == 12 and period == "am":
        hr = 0

    event_datetime = datetime.datetime(year, month, day, hr, min, tzinfo=timezone)

    print(event_datetime)
    # enforce a future time (ie. if they choose 3:00pm and its 11:59pm, then set day as tomorrow rather than taking today)
    if event_datetime < now:
        if not input_day:
            event_datetime += relativedelta.relativedelta(days=1)
        elif input_day and not input_month:
            event_datetime += relativedelta.relativedelta(months=1)
        elif input_day and input_month and not input_year:
            event_datetime += relativedelta.relativedelta(years=1)

    return event_datetime

# update active dict with new/changed timezone and write the new dictionary to JSON
# TODO: this should maybe only write to json on close instead of on every update
def update_timezone(id: int, timezone: str):
    user_timezones[str(id)] = timezone
    # opening the file with type 'w' causes writes (dump) to overwrite the entire file
    with open(TIMEZONE_JSON_DIR, "w") as f:
        json.dump(user_timezones, f)

# load token from .env and run bot
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
