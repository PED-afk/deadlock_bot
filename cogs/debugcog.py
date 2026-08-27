
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory, activeTimerExists, canUseCommand
from data_manage import save_json, load_json, load_txt
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID
from debug import readback, clean, printLog, printLogToDc

#

class Debug(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def check_cog(self, ctx, cog_name:str):
        if await canUseCommand(ctx):
            try:
                await self.bot.load_extension(f"cogs.{cog_name}")
            except commands.ExtensionAlreadyLoaded:
                await ctx.send("Cog is loaded")
            except commands.ExtensionNotFound:
                await ctx.send("Cog not found")
            else:
                await ctx.send("Cog is unloaded")
                await self.bot.unload_extension(f"cogs.{cog_name}")

    @commands.command()
    async def get_logs(self, ctx, what:str, delAfter:bool=False):
        if what==None:
            botcommands=[
                "`!get_logs all`: Everything.",
                "`!get_logs error`: Crash reports.",
                "`!get_logs log`: Debug logs.",
                "`!get_logs log_error`: Errors while triing to log.",
            ]
            await ctx.reply('\n'.join(botcommands))
        if await canUseCommand(ctx,1):
            await printLogToDc(self.bot,"dump",readback(what,delAfter))

    @commands.command()
    async def ping(self, ctx):
        if await canUseCommand(ctx,2):
            await ctx.reply("Pong!",delete_after=5)
                
    

async def setup(bot):
    await bot.add_cog(Debug(bot))


