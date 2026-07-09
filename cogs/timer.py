
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory

#"hidden" commands (they are not listed in bot_help; KEEP IT THIS WAY)
#"a secret for everyone"
#haha ... reference

class Hiddens(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.BOTS_CHANNEL_ID=bot.botchannel
          
    @bot.command()
    async def pause(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to pause a timer.")
                else:
                    if bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==False:
                        bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=True
                        await ctx.reply("Paused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                    else:
                        await ctx.reply("There isn't an active timer in this voice channel category or it's already paused.")
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
                        
    @bot.command()
    async def unpause(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to unpause a timer.")
                else:
                    if bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None and bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]==True:
                        bot.timers[ctx.author.voice.channel.category.name[-2]]["paused"]=False
                        await ctx.reply("Unpaused timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                    else:
                        await ctx.reply("There isn't an active timer in this voice channel category or it's already running.")
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
    
    @bot.command()
    async def start(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to be able to start a timer.")
                else:
                    if bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]==None:
                        bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=time.time()+bot.startTimers[ctx.author.voice.channel.category.name[-2]]
                        await ctx.reply("Started timer for the ["+ctx.author.voice.channel.category.name[-2]+"] category.")
                        
                        name=ctx.author.voice.channel.name[-2]
                        names=[]
                        for guild in bot.guilds:
                            for channel in discord.utils.get(guild.categories, name="["+name+"]").voice_channels:
                                for member in channel.members:
                                    if member.global_name=="PurpleEarthDragon":
                                        names.append(member.global_name+chooseFaceFromCategory(bot,"love"))
                                    else:
                                        names.append(member.global_name)
                        
                        await ctx.send("__Good luck, and Have fun!__\n"+'\n'.join(names)+"\n"+chooseFaceFromCategory(bot,"happy"),delete_after=bot.startTimers[ctx.author.voice.channel.category.name[-2]])
                    else:
                        await ctx.reply("There is already an active timer in this voice channel category.")
            else:
                await ctx.reply("You don't have permission! >:)",delete_after=10)
              
    @bot.command()
    async def end(ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel so I know which timer to end.")
                else:
                    if bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]>time.time()-1:
                        bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=time.time()-1
                        await ctx.reply("Timer stoped.")
    
    @bot.command()
    async def endit(ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel so I know which timer to end.")
                else:
                    if bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]!=None:
                        bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]=None
                        await ctx.reply("Timer stoped. Moving noone.")
    
    @bot.command()
    async def settimer(ctx,x:float):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to change a timer lenght.")
                else:
                    bot.startTimers[ctx.author.voice.channel.category.name[-2]]=x*60
                    await ctx.reply("Starting time set to "+str(x)+" minutes.")
                
    @bot.command()
    async def gettimer(ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to view a timer lenght.")
                else:
                    await ctx.reply("The timer is set to "+str(bot.startTimers[ctx.author.voice.channel.category.name[-2]]/60)+" minutes.")
                  
    
    @bot.command()
    async def remaining(ctx):
        if ctx.channel.id==BOTS_CHANNEL_ID:
            senderID=ctx.author.id
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.author.voice==None:
                    await ctx.reply("You must be in a voice channel to view a timer.")
                else:
                    if bot.startTimers[ctx.author.voice.channel.category.name[-2]]!=None:
                        await ctx.reply("Remaining time: "+str(round(abs(bot.timers[ctx.author.voice.channel.category.name[-2]]["time"]-time.time())/60,2))+" min(s).")
                    else:
                        await ctx.reply("Timer is not active.")

async def setup(bot):
    await bot.add_cog(Hiddens(bot))
