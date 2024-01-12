import discord
import zoneinfo
from .. import util

class TimezoneModal(discord.ui.Modal, title="Timezone Input"):
    tz = discord.ui.TextInput(label="Timezone", placeholder="eg. America/Vancouver")
    user_timezones: dict

    def __init__(self, user_timezones: dict):
        super().__init__()
        self.user_timezones = user_timezones
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # try creating a zoneinfo with the user input. if the input is bad, this will throw an error
            # the alternative is checking if self.tz.value in zoneinfo.all_timezones and not using try catch
            zoneinfo.ZoneInfo(self.tz.value)
            util.update_timezone(self.user_timezones, interaction.user.id, self.tz.value)
            await interaction.response.edit_message(content=f"You set your timezone to: '{self.tz}'. This message will be deleted in 5 seconds", view=None, delete_after=5.0)
        except Exception as e:
            print(e)
            # TODO: supposed to resend modal if input is bad but this doesnt work. find another way
            #await interaction.response.send_modal(self)
            await interaction.response.edit_message(content=f"bad input. TEMP MESSAGE ******", delete_after=5.0)