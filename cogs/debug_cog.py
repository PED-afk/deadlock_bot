
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import canUseCommand
from debug import readback, clean, printLog, printLogToDc
from constants import CUSTOM_MATCH_REMINDER_MESSAGE_BORDER,CUSTOM_MATCH_REMINDER_MESSAGE

from classes.button import Button, MultButton

#quess what this is for

class Debug(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def test(self,ctx):
        senderID=ctx.author.id
        if await canUseCommand(ctx,2):
            #await ctx.send("TEST:\nNothing to test.\n.=.",delete_after=10)
            #await ctx.reply(colorTextForDc("color?",Colors.PURPLE))
            #await ctx.reply(colorTextForDcRainbow("Rainbow with looooooooooooooooooooooooooooong text"))
            #await ctx.reply(colorTextForDcRainbow("Rainbow with looooooooooooooooooooooooooooong text and more letters the same",3))
            #view=Button()
            #view=MultButton(ctx.author)
            #view=FindRem(ctx,self.bot)
            #await ctx.send("Buttons:", view=view)
            await ctx.send(f"{''.join(CUSTOM_MATCH_REMINDER_MESSAGE_BORDER)}{CUSTOM_MATCH_REMINDER_MESSAGE}\n<link here>{''.join(reversed(CUSTOM_MATCH_REMINDER_MESSAGE_BORDER))}",delete_after=11)

    @commands.command()
    async def check_cog(self, ctx, cog_name:str):
        if await canUseCommand(ctx,2):
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
        if await canUseCommand(ctx,2):
            await printLogToDc(self.bot,"dump",readback(what,delAfter))

    @commands.command()
    async def ping(self, ctx):
        if await canUseCommand(ctx,2):
            await ctx.reply("Pong!",delete_after=5)
                
    

async def setup(bot):
    await bot.add_cog(Debug(bot))


