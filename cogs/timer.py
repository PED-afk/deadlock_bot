
import discord
from discord.ext import commands, tasks
import asyncio
import time

from own_utils import chooseFaceFromCategory, canUseCommand

#commands to control the timer function
#moved here from main file

class Timer(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def pause(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==False:
                self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=True
                await ctx.reply("Paused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
            else:
                await ctx.reply("There isn't an active timer in this voice channel category or it's already paused.")
                        
    @commands.command()
    async def unpause(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==True:
                self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=False
                await ctx.reply("Unpaused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
            else:
                await ctx.reply("There isn't an active timer in this voice channel category or it's already running.")
    
    @commands.command()
    async def start(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]==None:
                self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=time.time()+self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]
                await ctx.reply("Started timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                
                name=ctx.author.voice.channel.name[-2]
                names=[]
                for guild in self.bot.guilds:
                    for channel in discord.utils.get(guild.categories, name="["+name+"]").voice_channels:
                        for member in channel.members:
                            if member.global_name=="PurpleEarthDragon":
                                names.append(member.global_name+chooseFaceFromCategory(self.bot,"love"))
                            else:
                                names.append(member.global_name)
                
                await ctx.send("__Good luck, and Have fun!__\n"+'\n'.join(names)+"\n"+chooseFaceFromCategory(self.bot,"happy"),delete_after=self.bot.startTimers[ctx.author.voice.channel.category.name[-2]])
            else:
                await ctx.reply("There is already an active timer in this voice channel category.")
              
    @commands.command()
    async def end(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]>time.time()-1:
                self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=time.time()-1
                await ctx.reply("Timer stoped.")
    
    @commands.command()
    async def endit(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None:
                self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=None
                await ctx.reply("Timer stoped. Moving noone.")
    
    @commands.command()
    async def settimer(self,ctx,x:float):
        if await canUseCommand(ctx,1,True):
            self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]=x*60
            await ctx.reply("Starting time set to "+str(x)+" minutes.")
                
    @commands.command()
    async def gettimer(self,ctx):
        if await canUseCommand(ctx,1,True):
            await ctx.reply("The timer is set to "+str(self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]/60)+" minutes.")
                  
    
    @commands.command()
    async def remaining(self,ctx):
        if await canUseCommand(ctx,1,True):
            if self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]!=None:
                await ctx.reply("Remaining time: "+str(round(abs(self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]-time.time())/60,2))+" min(s).")
            else:
                await ctx.reply("Timer is not active.")

async def setup(bot):
    await bot.add_cog(Timer(bot))
