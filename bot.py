import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import User

class ReadyButtons(discord.ui.View): 
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def click_accept(self, interaction: discord.Interaction, button: discord.ui.button):
        #interaction.response.send_message("accept")
        #button.
        print("accepted")
    @discord.ui.button(label="❌", style=discord.ButtonStyle.blurple)
    async def click_decline(self, interaction: discord.Interaction, button: discord.ui.button):
        #interaction.response.send_message("decline")
        print("declined")
    @discord.ui.button(label="🤔", style=discord.ButtonStyle.blurple)
    async def click_maybe(self, interaction: discord.Interaction, button: discord.ui.button):
        #interaction.response.send_message("maybe?")
        print("maybed")

class ControlPanelButtons(discord.ui.view):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="ping everyone", row=1, style=discord.ButtonStyle.blurple)
    async def click_accept(self, interaction: discord.Interaction, button: discord.ui.button):
        #interaction.response.send_message("accept")
        #button.
        print("accepted")
    @discord.ui.button(label="cancel event", row=1, style=discord.ButtonStyle.blurple)
    async def click_decline(self, interaction: discord.Interaction, button: discord.ui.button):
        #interaction.response.send_message("decline")
        print("declined")

load_dotenv()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

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
@discord.app_commands.describe(event="What's happening?")
@discord.app_commands.describe(time="Does not need to follow any specific format; do whatever the participants will understand")
@discord.app_commands.describe(participants="Specify who you want to invite by mentioning them with @, similar to how you would ping them (eg. @kal @BenAstromo). Theres no need to include yourself.")
async def make_request(interaction: discord.Interaction, event: str, time: str, participants: str):
    embed = discord.Embed()
    embed.title = f'{event} at {time}'
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
        u = User(p_str)
        user_lst.append(u)
    
    return user_lst

token = os.getenv("DISCORD_TOKEN")
bot.run(token)
