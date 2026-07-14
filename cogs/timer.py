
import discord
from discord.ext import commands, tasks
import asyncio
import time

from own_utils import chooseFaceFromCategory
from dc_ids import ME,BOT_ROLE,BOTS_CHANNEL_ID

#commands to control the timer function
#moved here from main file

class Timer(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.BOTS_CHANNEL_ID=BOTS_CHANNEL_ID
        self.ME=ME
        self.BOT_ROLE=BOT_ROLE

    @commands.command()
    async def pause(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to pause a timer.")
                else:
                    if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==False:
                        self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=True
                        await ctx.reply("Paused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                    else:
                        await ctx.reply("There isn't an active timer in this voice channel category or it's already paused.")
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
                        
    @commands.command()
    async def unpause(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to unpause a timer.")
                else:
                    if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==True:
                        self.bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=False
                        await ctx.reply("Unpaused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                    else:
                        await ctx.reply("There isn't an active timer in this voice channel category or it's already running.")
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
    
    @commands.command()
    async def start(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to start a timer.")
                else:
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
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
              
    @commands.command()
    async def end(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel so I know which timer to end.")
                else:
                    if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]>time.time()-1:
                        self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=time.time()-1
                        await ctx.reply("Timer stoped.")
    
    @commands.command()
    async def endit(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel so I know which timer to end.")
                else:
                    if self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None:
                        self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=None
                        await ctx.reply("Timer stoped. Moving noone.")
    
    @commands.command()
    async def settimer(self,ctx,x:float):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to change a timer lenght.")
                else:
                    self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]=x*60
                    await ctx.reply("Starting time set to "+str(x)+" minutes.")
                
    @commands.command()
    async def gettimer(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to view a timer lenght.")
                else:
                    await ctx.reply("The timer is set to "+str(self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]/60)+" minutes.")
                  
    
    @commands.command()
    async def remaining(self,ctx):
        if ctx.channel.id==self.BOTS_CHANNEL_ID:
            senderID=ctx.author.id
            if senderID==self.ME or any(role.id == self.BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to view a timer.")
                else:
                    if self.bot.startTimers[ctx.author.voice.channel.category.name[-2]]!=None:
                        await ctx.reply("Remaining time: "+str(round(abs(self.bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]-time.time())/60,2))+" min(s).")
                    else:
                        await ctx.reply("Timer is not active.")

async def setup(bot):
    await bot.add_cog(Timer(bot))
