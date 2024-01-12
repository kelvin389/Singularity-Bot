import discord
import zoneinfo
#from ..bot import update_timezone

# TODO: for some reason the title doesnt work
class TimezoneModal(discord.ui.Modal, title="Input your timezone"):
    tz = discord.ui.TextInput(label="Timezone", placeholder="eg. America/Vancouver")

    def __init__(self):
        super().__init__()
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # try creating a zoneinfo with the user input. if the input is bad, this will throw an error
            # the alternative is checking if self.tz.value in zoneinfo.all_timezones and not using try catch
            zoneinfo.ZoneInfo(self.tz.value)
            #update_timezone(interaction.user.id, self.tz.value)
            await interaction.response.edit_message(content=f"You set your timezone to: '{self.tz}'. This message will be deleted in 5 seconds", delete_after=5.0)
        except:
            # TODO: supposed to resend modal if input is bad but this doesnt work. find another way
            #await interaction.response.send_modal(self)
            None