import discord
from ..modals.timezone_modal import TimezoneModal

class TimezoneButtons(discord.ui.View):
    tz_modal: discord.ui.Modal

    def __init__(self, tz_modal: discord.ui.Modal):
        super().__init__()
        self.tz_modal = tz_modal

        link_button = discord.ui.Button(label="link", style=discord.ButtonStyle.blurple, url="https://kevinnovak.github.io/Time-Zone-Picker/")
        self.add_item(link_button)
    
    @discord.ui.button(label="input", style=discord.ButtonStyle.blurple)
    async def click_input(self, interaction: discord.Interaction, button: discord.ui.button):
        await interaction.response.send_modal(self.tz_modal)