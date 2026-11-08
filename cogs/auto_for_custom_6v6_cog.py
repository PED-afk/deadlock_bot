
import discord
from discord.ext import commands, tasks
import datetime

from own_utils import chooseFaceFromCategory, canUseCommand
from debug import printLogToDc, printLog
from classes.bot_faces import Faces
from constants import CHANNEL_IDS, ROLES
from constants import CUSTOM_MATCH_ORGANIZE_MESSAGE, FUNLOCK_SERVER_ID
from data_manage import deep_save_txt
from classes.file_paths import BotPaths

#automated funtionality for custom matches on the weekend

class AutoOrganizer(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    async def cog_load(self):
        self.tick.start()

    async def cog_unload(self):
        self.tick.cancel()
    
    @commands.command()
    async def removeCustomMatchRole(self,ctx):
        guild=self.bot.get_guild(FUNLOCK_SERVER_ID)
        role = guild.get_role(ROLES.CUSTOM_MATCH)
        if role is None:
            print("Role not found!")
            return
        for member in role.members:
            try:
                await member.remove_roles(role, reason="Automatic role cleanup")
            except discord.Forbidden:
                print(f"Missing permissions to remove role from {member}")
            except discord.HTTPException as e:
                print(f"Failed to remove role from {member}: {e}")
        print(f"Removed {role.name} from everyone.")

        

    def nextMatchMessage(self):
        now=datetime.datetime.now(datetime.timezone.utc)
        valid_days=[4, 5, 6]
        days_until=min((day-now.weekday())%7 for day in valid_days)
        next_match=(now+datetime.timedelta(days=days_until)).replace(
            hour=20,
            minute=0,
            second=0,
            microsecond=0
        )

        if next_match<=now:
            next_match+=datetime.timedelta(days=1)
            while next_match.weekday() not in valid_days:
                next_match+=datetime.timedelta(days=1)

        return int(next_match.timestamp())

    @tasks.loop(seconds=1)
    async def tick(self):
        now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        if self.bot.organizedMessageTime==None or now-self.bot.organizedMessageTime>=7*24*60*60:
            channel=self.bot.get_channel(CHANNEL_IDS.LOUNGE_CHANNEL_ID)
            if channel:
                self.bot.organizedMessageTime=self.nextMatchMessage()
                deep_save_txt(BotPaths.autoOrgTimeStamp_file,str(self.bot.organizedMessageTime))
                msg=CUSTOM_MATCH_ORGANIZE_MESSAGE.replace("÷",str(self.bot.organizedMessageTime))
                message=await channel.send(msg)
                self.organizedMessageID=message.id

async def setup(bot):
    await bot.add_cog(AutoOrganizer(bot))
