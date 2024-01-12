import discord
from ..objs.Event import Event
from ..objs.User import User
from .control_panel_buttons import ControlPanelButtons
from .ready_buttons import ReadyButtons

class ConfirmationButtons(discord.ui.View):
    event_obj: Event

    def __init__(self, event_obj: Event):
        super().__init__()
        self.event_obj = event_obj 

    @discord.ui.button(label="✅", style=discord.ButtonStyle.blurple)
    async def click_confirm(self, interaction: discord.Interaction, button: discord.ui.button):
        # send all users a copy of the message
        for u in self.event_obj.users:
            user = u.discord_user
            
            # send the host control panel buttons, other participants ready buttons
            if u.status == User.STATUS_HOST:
                cp_buttons = ControlPanelButtons(self.event_obj)
                msg = await user.send(embed=self.event_obj.embed, view=cp_buttons)
                u.status_message = msg
            else:
                ready_buttons = ReadyButtons(self.event_obj)
                msg = await user.send(embed=self.event_obj.embed, view=ready_buttons)
                u.status_message = msg
    
        await interaction.response.edit_message(content="Event successfully set up. This message will be deleted in 5 seconds", embed=None, view=None, delete_after=5.0)
    @discord.ui.button(label="❌", style=discord.ButtonStyle.blurple)
    async def click_reject(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.edit_message(content="Event not set up. This message will be deleted in 5 seconds", embed=None, view=None, delete_after=5.0)