

import discord
from discord.ext import commands

from debug import printLog,printLogToDc

from classes.shop import Shop




class ChooseShopCategory(discord.ui.View):
    def __init__(self, ctx, bot:commands.Bot):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = ctx.author
        self.bot=bot

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True)
            return False
        return True


    @discord.ui.button(label="Weapon", style=discord.ButtonStyle.primary,row=0)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopTier(self.ctx,self.bot,"weapon")
        await interaction.response.send_message("Weapon",view=view,delete_after=120.0,ephemeral=True)
        
    @discord.ui.button(label="Vitality", style=discord.ButtonStyle.primary,row=0)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopTier(self.ctx,self.bot,"vitality")
        await interaction.response.send_message("Vitality",view=view,delete_after=120.0,ephemeral=True)
        
    @discord.ui.button(label="Spirit", style=discord.ButtonStyle.primary,row=0)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopTier(self.ctx,self.bot,"spirit")
        await interaction.response.send_message("Spirit",view=view,delete_after=120.0,ephemeral=True)


class ChooseShopTier(discord.ui.View):
    def __init__(self, ctx, bot:commands.Bot,itemType):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = ctx.author
        self.bot=bot
        self.itemType=itemType

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True)
            return False
        return True


    @discord.ui.button(label="Tier I", style=discord.ButtonStyle.primary,row=0)
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopItem(self.ctx,self.bot,self.itemType,1)
        await interaction.response.send_message("Tier I",view=view,delete_after=120.0,ephemeral=True)
        
    @discord.ui.button(label="Tier II", style=discord.ButtonStyle.primary,row=0)
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopItem(self.ctx,self.bot,self.itemType,2)
        await interaction.response.send_message("Tier II",view=view,delete_after=120.0,ephemeral=True)
        
    @discord.ui.button(label="Tier III", style=discord.ButtonStyle.primary,row=0)
    async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopItem(self.ctx,self.bot,self.itemType,3)
        await interaction.response.send_message("Tier III",view=view,delete_after=120.0,ephemeral=True)
        
    @discord.ui.button(label="Tier IV", style=discord.ButtonStyle.primary,row=0)
    async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
        view=ChooseShopItem(self.ctx,self.bot,self.itemType,4)
        await interaction.response.send_message("Tier IV",view=view,delete_after=120.0,ephemeral=True)


class ChooseShopItem(discord.ui.View):
    def __init__(self, ctx, bot:commands.Bot,category:str,tier:int):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.author = ctx.author
        self.bot=bot
        self.tier=tier
        self.itemType=category

        c=0
        for item in self.bot.items:
            #printLog("debug",str(item.tier)+"; "+str(self.tier)+"; "+str(item.type)+"; "+str(self.itemType))
            if item.tier==self.tier and item.type==self.itemType:
                button=discord.ui.Button(label=item.name,style=discord.ButtonStyle.primary,row=c//5)
                c+=1

                async def callback(interaction: discord.Interaction,item=item):
                    cost=Shop().getCost(self.tier)
                    if cost<=self.bot.user_data[str(ctx.author.id)]["money"]["secured"]:
                        await interaction.response.send_message(f"{self.author.mention} bought {item.name}")
                        self.bot.user_data[str(ctx.author.id)]["money"]["secured"]-=cost
                        self.bot.user_data[str(ctx.author.id)]["item"].append(item)
                    else:
                        await interaction.response.send_message(f"You can not afford {item.name}.\nYour secured souls: {self.bot.user_data[str(ctx.author.id)]["money"]["secured"]}\nItem cost: {cost}",delete_after=120.0,ephemeral=True)

                button.callback=callback
                self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id!=self.author.id:
            await interaction.response.send_message("You can't use these buttons.",ephemeral=True)
            return False
        return True






