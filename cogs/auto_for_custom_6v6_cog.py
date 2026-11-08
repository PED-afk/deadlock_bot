
import discord
from discord.ext import commands, tasks
import datetime

from own_utils import chooseFaceFromCategory, canUseCommand
from debug import printLogToDc, printLog
from classes.bot_faces import Faces
from constants import CHANNEL_IDS, ROLES

#automated funtionality for custom matches on the weekend

class AutoOrganizer(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    async def cog_load(self):
        self.tick.start()

    async def cog_unload(self):
        self.tick.cancel()
    
    @commands.command()
    async def a(self,ctx):
        pass

    def nextMatchMessage(self):
        now=datetime.datetime.now(datetime.timezone.utc)
        days_until_saturday=(5-now.weekday())%7

        if days_until_saturday==0:
            days_until_saturday=7

        next_saturday=now+datetime.timedelta(days=days_until_saturday)
        timestamp=int(next_saturday.timestamp())

        return timestamp

    @tasks.loop(seconds=1)
    async def tick(self):
        now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        if self.bot.organizedMessageTime==None or now-self.bot.organizedMessageTime>=7*24*60*60:
            channel=self.bot.get_channel(CHANNEL_IDS.LOUNGE_CHANNEL_ID)
            if channel:
                self.bot.organizedMessageTime=self.nextMatchMessage()
                await channel.send(f"<@&{ROLES.CUSTOM_MATCH}>\nThere will be a custom match at: <t:{self.bot.organizedMessageTime}:F>\nThis is a test for now.")

async def setup(bot):
    await bot.add_cog(AutoOrganizer(bot))
