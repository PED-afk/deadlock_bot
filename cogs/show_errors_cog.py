
import discord
from discord.ext import commands, tasks
import asyncio
import time
import random

from own_utils import chooseFaceFromCategory
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from classes.bot_faces import Faces

#tell people (who need to know) about things going wrong

class ErrorOverwrite(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_error(self,event, *args, **kwargs):
        import sys
        exc_type, exc, tb = sys.exc_info()

        printLogToDc(self.bot,"error",f"Exception in event: {event}")
        import traceback
        traceback.print_exception(exc_type, exc, tb)
        
        
    @commands.Cog.listener()
    async def on_command_error(self,ctx, error):
        await printLogToDc(self.bot,"error",f"Command error: {error}")


async def setup(bot):
    await bot.add_cog(ErrorOverwrite(bot))
