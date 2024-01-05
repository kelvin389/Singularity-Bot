# Standard Library Imports
import os
import re
import datetime

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

# Update all user's status messages when someone changes their status
async def update_status(interaction: discord.Interaction, new_status: int, event_obj: Event.Event):
    user_id = interaction.user.id # id of the user who wants to change their status
    user_lst = event_obj.users

    # update users status
    for u in user_lst:
        if u.id == user_id:
            u.set_status(new_status)
            break

    # Modify the embed with new status
    event_obj.update_embed_statuses()

    # Edit everyones event message with new embed
    for u in event_obj.users:
        if u.status == User.STATUS_HOST:
            cp_buttons = ControlPanelButtons(event_obj)
            await u.status_message.edit(embed=event_obj.embed, view=cp_buttons)
        else:
            ready_buttons = ReadyButtons(event_obj)
            await u.status_message.edit(embed=event_obj.embed, view=ready_buttons)

class ReadyButtons(discord.ui.View): 
    event_obj: Event.Event

    def __init__(self, event_obj: Event.Event):
        super().__init__()
        self.event_obj = event_obj

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def click_accept(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_ACCEPTED, self.event_obj)
        await interaction.response.defer()
    @discord.ui.button(label="❌", style=discord.ButtonStyle.blurple)
    async def click_reject(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_REJECTED, self.event_obj)
        await interaction.response.defer()
    @discord.ui.button(label="🤔", style=discord.ButtonStyle.blurple)
    async def click_maybe(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_MAYBE, self.event_obj)
        await interaction.response.defer()

class ControlPanelButtons(discord.ui.View):
    event_obj: Event.Event

    def __init__(self, event_obj: Event.Event):
        super().__init__()
        self.event_obj = event_obj 

    @discord.ui.button(label="Ping Participants", row=1, style=discord.ButtonStyle.blurple)
    async def click_ping(self, interaction: discord.Interaction, button: discord.ui.button):
        host_id = interaction.user.id
        for u in self.event_obj.users:
            if u.id != host_id:
                user = bot.get_user(u.id) 
                await user.send(f'<@{host_id}> pinged you!')
        await interaction.response.send_message(f'You pinged all participants')
        print(f'{u.host} pinged all participants') # this is not working right now

    @discord.ui.button(label="Cancel Event", row=1, style=discord.ButtonStyle.blurple)
    async def click_cancel(self, interaction: discord.Interaction, button: discord.ui.button):
        host_id = interaction.user.id
        for u in self.event_obj.users:
            await u.status_message.edit(embed=discord.Embed(title=f'Event Cancelled'))
            if u.id != host_id:
                user = bot.get_user(u.id)
                await user.send(f'<@{host_id}> has cancelled the event')
        await interaction.response.send_message("Cancel successful")
        print(f'{host_id} canceled event')

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

    # format of the time that will be shown to users
    embed_strftime = "%I:%M %p"
    if day: # show month and day if a day was inputted
        embed_strftime += ", %b. %d"
    if year: # show year if year was inputted
        embed_strftime += ", %Y"

    event_datetime = to_datetime(time, day, month, year)
    event_timestamp = int(event_datetime.timestamp()) # event time in unix timestamp format

    embed = discord.Embed()
    embed.title = f'{event} at {event_datetime.strftime(embed_strftime)} (<t:{event_timestamp}:R>)'
    embed.colour = discord.Colour.blue()
    embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/original/001/708/596/db3.jpeg")
    embed.set_footer(text="!note [message] to leave a note")

    participants = participants.strip() # list of participants each in format "<@[id]>"
    participants_lst = participants.split() # split with no args splits on all whitespace (multiple spaces, newlines, etc)
    inital_user_lst = participants_to_users(interaction.user.id, participants_lst)
    event_obj = Event.Event(event, inital_user_lst, embed)

    # send all users a copy of the message
    for u in event_obj.users:
        user = bot.get_user(u.id)
        
        # send the host control panel buttons, other participants ready buttons
        if u.status == User.STATUS_HOST:
            cp_buttons = ControlPanelButtons(event_obj)
            msg = await user.send(embed=embed, view=cp_buttons)
            u.status_message = msg
        else:
            ready_buttons = ReadyButtons(event_obj)
            msg = await user.send(embed=embed, view=ready_buttons)
            u.status_message = msg

    await interaction.response.send_message("Event successfully set up.", ephemeral=True)

# convert host and list of participants to a list of users.
# host is int, participants list is list of strings: ["<@[id1]>", "<@[id2]>", ...]
def participants_to_users(host, participants_lst): 
    user_lst = []   

    host_u = User.User(host, True)
    user_lst.append(host_u)
    # turn participants list into User object list
    for p_str in participants_lst:
        u = User.User(p_str)
        user_lst.append(u)
    
    return user_lst

def to_datetime(time: str, input_day: int, input_month: int, input_year: int):
    now = datetime.datetime.now()

    day = input_day if input_day else now.day
    month = input_month if input_month else now.month
    year = input_year if input_year else now.year
    
    # regex magic to extract the 2 (+1 optional) components from time string (11:59pm -> pulls out 11, 59, pm)
    match = re.match(r"^(\d{1,2}):(\d{2})\s?([apAP][mM])?$", time)
    hr, min, period = int(match.group(1)), int(match.group(2)), match.group(3)
    # account for 12 hr time format.
    # period will be discarded if a 24hr time is inputted with period (eg. 15:00am will be taken as 15:00 = 3:00pm)
    if hr <= 12 and period and period.lower() == "pm":
        hr += 12

    # TODO: convert datetime obj by timezone
    event_datetime = datetime.datetime(year, month, day, hr, min)

    # enforce a future time (ie. if they choose 3:00pm and its 11:59pm, then set day as tomorrow rather than taking today)
    if not input_day:
        event_datetime += relativedelta.relativedelta(days=1)
    elif input_day and not input_month:
        event_datetime += relativedelta.relativedelta(months=1)
    elif input_day and input_month and not input_year:
        event_datetime += relativedelta.relativedelta(years=1)

    return event_datetime

# load token from .env and run bot
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
