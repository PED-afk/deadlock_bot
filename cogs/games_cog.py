

import discord
from discord.ext import commands, tasks

from own_utils import chooseFaceFromCategory, canUseCommand
from constants import CHANNEL_IDS
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from classes.shop_views import ChooseShopCategory

#tools for everyone

class Games(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def shop(self,ctx):
        if await canUseCommand(ctx,3):
            view=ChooseShopCategory(ctx,self.bot)
            await ctx.reply("Choose a shop category:", view=view, ephemeral=True, delete_after=120.0)


   
async def setup(bot):
    await bot.add_cog(Games(bot))
