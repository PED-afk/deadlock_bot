
import discord
from discord.ext import commands, tasks
import asyncio
import time
import random

from own_utils import chooseFaceFromCategory
from constants import CHANNEL_IDS, PRIVATE_MESSAGE_CONTENT
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from classes.bot_faces import Faces

#what to do when someone new joins

class MemberJoin(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_member_join(self,member):
        try:
            cont=PRIVATE_MESSAGE_CONTENT
            cont=cont.replace("#0#",self.bot.get_channel(CHANNEL_IDS.RULES_CHANNEL_ID).mention)
            cont=cont.replace("#1#",self.bot.get_channel(CHANNEL_IDS.ROLE_CHANNEL_ID).mention)
            cont=cont.replace("#2#",self.bot.get_channel(CHANNEL_IDS.FLOOR_PLAN_CHANNEL_ID).mention)
            cont=cont.replace("#3#",self.bot.get_channel(CHANNEL_IDS.SUGGESTIONS_CHANNEL_ID).mention)
            cont=cont.replace("#f#",chooseFaceFromCategory(Faces.big_eyes))
            embed = discord.Embed(title="Welcome To Funlock",description=(PRIVATE_MESSAGE_CONTENT),color=discord.Color.purple())

            # Image/GIF on the right side
            embed.set_thumbnail(url="https://klipy.com/gifs/rem-rem-deadlock")

            await member.send("Welcome!",embed=embed)
        except discord.Forbidden:
            printLog("exception",f"Couldn't DM {member} — their DMs may be disabled.")

async def setup(bot):
    await bot.add_cog(MemberJoin(bot))
