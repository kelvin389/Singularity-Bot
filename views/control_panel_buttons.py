import discord
from .. import Event

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
                user = u.discord_user
                await user.send(f"<@{host_id}> pinged you!")
        await interaction.response.send_message(f"You pinged all participants")
        print(f"{host_id} pinged all participants")

    @discord.ui.button(label="Cancel Event", row=1, style=discord.ButtonStyle.blurple)
    async def click_cancel(self, interaction: discord.Interaction, button: discord.ui.button):
        cancelled_embed = discord.Embed(title="Event Cancelled")
        host_id = interaction.user.id
        
        for u in self.event_obj.users:
            await u.status_message.edit(embed=cancelled_embed, view=None)

            if u.id != host_id:
                user = u.discord_user
                await user.send(f"<@{host_id}> has cancelled the event")
        await interaction.response.send_message("Cancel successful")
        print(f"{host_id} cancelled event")