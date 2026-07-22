

import discord
from discord.ext import commands
import random

class FindRem(discord.ui.View):
    def __init__(self, ctx, bot:commands.bot):
        super().__init__(timeout=60)  #expire in 60 sec
        self.ctx = ctx
        self.author = ctx.author
        self.bot=bot
        
        self.buttonTexts=[]
        for i in range(9):
            if random.randint(0,2)==0:
                self.buttonTexts.append("Nothing\nBut money!")
            else:
                self.buttonTexts.append("Nothing...")
        rRem=random.randint(0,8)
        self.buttonTexts[rRem]=":blue_circle: :blue_circle:\nA lot of money!\n"
        rBird=random.randint(0,8)
        rBird2=random.randint(0,4)
        if rBird%4==rBird2 and rRem!=rBird:
            self.buttonTexts[rBird]="OH oh...\n:green_circle::owl:\n"
        
        posibleLabels=[
            "yellow walker",
            "yellow guardian",
            "blue walker",
            "blue guardian",
            "green walker",
            "green guardian",
            "yellow sinner",
            "green sinner",
            "blue left sinner",
            "blue right sinner",
            "enemy double sinner",
            "friendly double sinner",
            "yellow secret shop",
            "green secret shop",
            "midboss",
            "yellow bridgebuff",
            "green bridgebuff",
            "yellow teleporter",
            "green teleporter"
        ]
        self.labels=[]
        for i in range(9):
            r=random.randint(0,len(posibleLabels)-1)
            self.labels.append(posibleLabels[r])
            posibleLabels.pop(r)
        self.button1.label = self.labels[0]
        self.button2.label = self.labels[1]
        self.button3.label = self.labels[2]
        self.button4.label = self.labels[3]
        self.button5.label = self.labels[4]
        self.button6.label = self.labels[5]
        self.button7.label = self.labels[6]
        self.button8.label = self.labels[7]
        self.button9.label = self.labels[8]

    def resoultEval(self,buttonText):
        bot=self.bot
        authorID=str(self.author.id)
        if ":blue_circle:" in buttonText:
            r=random.randint(4,10)
            bot.user_data[authorID]["money"]["unsecured"]+=r*100
            return ("The Rem gave you "+str(r*100)+" souls.")
        elif buttonText=="Nothing\nBut money!":
            r=random.randint(1,3)
            bot.user_data[authorID]["money"]["secured"]+=r*100
            return ("You got "+str(r*100)+" souls.")
        elif ":green_circle::owl:" in buttonText:
            moneyLost=bot.user_data[authorID]["money"]["unsecured"]
            bot.user_data[authorID]["money"]["unsecured"]=0
            return ("You died and lost "+str(moneyLost)+" unsecured souls.")
        elif buttonText=="Nothing...":
            return ("Nothing...")
        return "Something went wrong"

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True)
            return False
        return True
    
    #, emoji=""

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary,row=0)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[0]+"\n"+self.resoultEval(self.buttonTexts[0]))
        
    @discord.ui.button(label="2", style=discord.ButtonStyle.primary,row=0)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[1]+"\n"+self.resoultEval(self.buttonTexts[1]))
        
    @discord.ui.button(label="3", style=discord.ButtonStyle.primary,row=0)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[2]+"\n"+self.resoultEval(self.buttonTexts[2]))

        
    @discord.ui.button(label="4", style=discord.ButtonStyle.primary,row=1)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[3]+"\n"+self.resoultEval(self.buttonTexts[3]))
        
    @discord.ui.button(label="5", style=discord.ButtonStyle.primary,row=1)
    async def button5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[4]+"\n"+self.resoultEval(self.buttonTexts[4]))
        
    @discord.ui.button(label="6", style=discord.ButtonStyle.primary,row=1)
    async def button6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[5]+"\n"+self.resoultEval(self.buttonTexts[5]))
        
        
    @discord.ui.button(label="7", style=discord.ButtonStyle.primary,row=2)
    async def button7(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[6]+"\n"+self.resoultEval(self.buttonTexts[6]))
        
    @discord.ui.button(label="8", style=discord.ButtonStyle.primary,row=2)
    async def button8(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[7]+"\n"+self.resoultEval(self.buttonTexts[7]))
        
    @discord.ui.button(label="9", style=discord.ButtonStyle.primary,row=2)
    async def button9(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message(self.buttonTexts[8]+"\n"+self.resoultEval(self.buttonTexts[8]))