import discord
from ..modals.timezone_modal import TimezoneModal

class TimezoneButtons(discord.ui.View):
    def __init__(self):
        super().__init__()

        link_button = discord.ui.Button(label='link to choose', style=discord.ButtonStyle.blurple, url="https://kevinnovak.github.io/Time-Zone-Picker/")
        self.add_item(link_button)
    
    @discord.ui.button(label="input", style=discord.ButtonStyle.blurple)
    async def click_reject(self, interaction: discord.Interaction, button: discord.ui.button):
        tz_modal = TimezoneModal()
        await interaction.response.send_modal(tz_modal)