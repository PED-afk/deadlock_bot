
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory, activeTimerExists, canUseCommand
from data_manage import save_json, load_json, load_txt
from dc_ids import ME,BOT_ROLE,BOTS_CHANNEL_ID
from debug import readback, clean

#

class Debug(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def check_cogs(self, ctx, cog_name):
        if canUseCommand(ctx):
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
        if canUseCommand(ctx,1):
            readback(what,delAfter)
                
    

async def setup(bot):
    await bot.add_cog(Debug(bot))


