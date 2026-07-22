

import discord

class Button(discord.ui.View):
    @discord.ui.button(label="Click Me", style=discord.ButtonStyle.primary)
    async def button_callback(self,interaction: discord.Interaction,button: discord.ui.Button):
        #await interaction.response.send_message("Button!",ephemeral=True) #only clicker sees
        await interaction.response.send_message("Button!")

        
class MultButton(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__(timeout=60)  #expire in 60 sec
        self.author = author

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="1", style=discord.ButtonStyle.success)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message("1!")
        
    @discord.ui.button(label="2", style=discord.ButtonStyle.danger)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message("2!")