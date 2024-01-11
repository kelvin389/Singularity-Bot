import discord
import zoneinfo
#from ..bot import update_timezone

# TODO: for some reason the title doesnt work
class TimezoneModal(discord.ui.Modal, title="ASDFASDFASDF DFQW FQW EF WQDFAS DF"):
    tz = discord.ui.TextInput(label="Timezone", placeholder="eg. America/Vancouver")

    def __init__(self):
        super().__init__()
        self.title = ""
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            zoneinfo.ZoneInfo(self.tz.value)
            #update_timezone(interaction.user.id, self.tz.value)
            await interaction.response.edit_message(content=f"You set your timezone to: '{self.tz}'. This message will be deleted in 5 seconds", delete_after=5.0)
        except:
            interaction.response.send_modal(self)