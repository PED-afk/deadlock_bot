
import discord
from discord.ext import commands, tasks

from own_utils import chooseFaceFromCategory, canUseCommand
from debug import printLogToDc, printLog
from classes.bot_faces import Faces

#fun little commands but they aren't hidden

class Funs(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    
    @commands.command()
    async def gl(self,ctx):
        if await canUseCommand(ctx,3,False,False,False):
            if ctx.author.voice==None:
                await ctx.reply(f"<@{ctx.author.id}> is wishing the others, Good luck and Have fun!"+chooseFaceFromCategory(Faces.FaceBigCategory.happies))
            else:
                channel = ctx.author.voice.channel
                members=[]
                for member in channel.members:
                    members.append(member.id)
                allM=""
                for i in members:
                    allM+=f"<@{i}>"
                await ctx.reply(f"<@{ctx.author.id}> is wishing \n{allM}, Good luck and Have fun!{chooseFaceFromCategory(Faces.FaceBigCategory.happies)}")
        ctx.message.delete

async def setup(bot):
    await bot.add_cog(Funs(bot))
