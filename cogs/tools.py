

import discord
from discord.ext import commands, tasks
import asyncio
import time
import random

from own_utils import chooseFaceFromCategory, canUseCommand
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID, WHO_AM_I_ROLES
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths

#tools for everyone

class Tools(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def onlines(self,ctx):
        if canUseCommand(ctx,3,inChannel=False):
            role_id=WHO_AM_I_ROLES["ping_if_online"]["id"]

            role=ctx.guild.get_role(role_id)
            if role is None:
                printLog("error","`ping if online` role not found.")
                return
            online_members=[member.mention for member in role.members if member.status == discord.Status.online and member.id!=ctx.author.id]
            mentions="\n".join(online_members)

            if len(online_members)!=0:
                message=f"{ctx.author.mention} is looking for people to play with!\n\n{mentions}"
                await ctx.send(message)
            else:
                await ctx.reply("No users online.")


   
async def setup(bot):
    await bot.add_cog(Tools(bot))
