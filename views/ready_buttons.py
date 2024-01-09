import discord
from .. import Event, User

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
        await u.status_message.edit(embed=event_obj.embed)

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