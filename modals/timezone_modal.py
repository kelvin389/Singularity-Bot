import discord
from ..bot import update_timezone

# TODO: for some reason the title doesnt work
# TODO: move this to a new file
class TimezoneModal(discord.ui.Modal, title="ASDFASDFASDF DFQW FQW EF WQDFAS DF"):
    tz = discord.ui.TextInput(label="Timezone", placeholder="eg. America/Vancouver")

    def __init__(self):
        super().__init__()
        self.title = ""
    
    async def on_submit(self, interaction: discord.Interaction):
        update_timezone(interaction.user.id, self.tz.value)
        await interaction.response.send_message(f"you entered {self.tz}", ephemeral=True)