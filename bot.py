import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import User
import datetime
import re

async def update_status(interaction: discord.Interaction, new_status: int):
    user_id = interaction.user.id
    await interaction.message.edit(embed=discord.Embed(title=f"new shit here new status:{new_status}"))
    # TODO: get the user object that matches user_id and update its status

class ReadyButtons(discord.ui.View): 
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def click_accept(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_ACCEPTED)
        await interaction.response.send_message("Your status has been updated to ✅")
    @discord.ui.button(label="❌", style=discord.ButtonStyle.blurple)
    async def click_reject(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_REJECTED)
        await interaction.response.send_message("Your status has been updated to ❌")
    @discord.ui.button(label="🤔", style=discord.ButtonStyle.blurple)
    async def click_maybe(self, interaction: discord.Interaction, button: discord.ui.button):
        await update_status(interaction, User.STATUS_MAYBE)
        await interaction.response.send_message("Your status has been updated to 🤔")

class ControlPanelButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="ping everyone", row=1, style=discord.ButtonStyle.blurple)
    async def click_ping(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message("pinggg")
        # TODO: figure out where to get 'users' (list of all User objects)
        #for u in users:
            #u.discord_user.send("PING!!!")
        print("ping")
    @discord.ui.button(label="cancel event", row=1, style=discord.ButtonStyle.blurple)
    async def click_cancel(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_message("event cancel")
        print("cancel")

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

    now = datetime.datetime.now()
    embed_strftime = "%I:%M %p"

    # TODO: dogshit code
    if not day:
        day = now.day
    else:
        # if a day is set, then also show a day and month in the embed
        embed_strftime += ", %b. %d"
    if not month:
        month = now.month
    if not year:
        year = now.year
    else:
        # also show year in embed if its set
        embed_strftime += ", %Y"
    
    # regex magic to extract the 2 (+1 optional) components from time string (11:59pm -> pulls out 11, 59, pm)
    match = re.match(r"^(\d{1,2}):(\d{2})\s?([apAP][mM])?$", time)
    hr, min = int(match.group(1)), int(match.group(2))
    # account for 12 hr time format
    # TODO: fix if 24 hr time is inputted and pm (eg. 15:00pm)
    if match.group(3) and match.group(3).lower() == "pm":
        hr += 12

    # TODO: convert datetime obj by timezone
    event_datetime = datetime.datetime(year, month, day, hr, min)

    # enforce a future time (ie. if they choose 3:00pm and its 11:59pm, then set day as tomorrow rather than taking today)
    # TODO: only works for rolling over a day. possibly also roll over month/syears
    # TODO: worst way of doing this of all time
    while (event_datetime < now):
        event_datetime += datetime.timedelta(days=1)

    event_timestamp = int(event_datetime.timestamp())
    embed = discord.Embed()
    embed.title = f'{event} at {event_datetime.strftime(embed_strftime)} (<t:{event_timestamp}:R>)'
    embed.colour = discord.Colour.blue()
    embed.set_thumbnail(url="https://i.kym-cdn.com/photos/images/original/001/708/596/db3.jpeg")
    embed.set_footer(text="!note [message] to leave a note")

    print("event: ", event)
    print("time: ", time)
    print("participants: ", participants)

    # list of participants each in format "<@[id]>"
    participants = participants.strip()
    participants_lst = participants.split() # split with no args splits on all whitespace (multiple spaces, newlines, etc)
    user_lst = participants_to_users(interaction.user.id, participants_lst)

    # construct list of users with their respective emojis
    embed_str = ''
    for u in user_lst:
        embed_str += f'{u.emoji}{u.id_str} {u.note}\n'
    embed.add_field(name="Participants", value=embed_str, inline=True)

    ready_buttons = ReadyButtons()
    # send all users a copy of the message
    for u in user_lst:
        user = bot.get_user(u.id)
        
        # send the host control panel buttons, other participants ready buttons
        if u.status == User.STATUS_HOST:
            cp_buttons = ControlPanelButtons()
            await user.send(embed=embed, view=cp_buttons)
        else:
            ready_buttons = ReadyButtons()
            await user.send(embed=embed, view=ready_buttons)

    await interaction.response.send_message("Event successfully set up. ", ephemeral=True)


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

# load token from .env and run bot
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
