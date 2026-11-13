
import discord
from discord.ext import commands, tasks
import datetime

from own_utils import chooseFaceFromCategory, canUseCommand, removeRoleFromEveryone
from debug import printLogToDc, printLog
from classes.bot_faces import Faces
from constants import CHANNEL_IDS, ROLES
from constants import CUSTOM_MATCH_ORGANIZE_MESSAGE, FUNLOCK_SERVER_ID, CUSTOM_MATCH_REMINDER_MESSAGE,CUSTOM_MATCH_REMINDER_MESSAGE_BORDER
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
        if not await canUseCommand(ctx,1):
            return
        guild=self.bot.get_guild(FUNLOCK_SERVER_ID)
        role = guild.get_role(ROLES.CUSTOM_MATCH_PART)
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
        await ctx.reply(f"Removed {role.name} from everyone.")

        

    def nextMatchMessageTimeStamp(self):
        """
        returns the timestamp of the next valid date for a custom match
        """
        
        now=datetime.datetime.now(datetime.timezone.utc)
        valid_days=[4, 5, 6]
        #no friday
        valid_days=[5, 6]
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

    @tasks.loop(seconds=3600)
    async def tick(self):
        async def message_exists(channel:discord.TextChannel, message_id: int) -> bool:
            try:
                await channel.fetch_message(message_id)
                return True
            except discord.NotFound:
                return False
        channelID=CHANNEL_IDS.PA_ID
        mentionChannelID=CHANNEL_IDS.LOUNGE_CHANNEL_ID
        now=int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        c=await self.bot.fetch_channel(channelID)
        oldMessageExists=self.bot.organizedMessageID is not None and await message_exists(c,self.bot.organizedMessageID)
        if self.bot.organizedMessageTime is None or self.bot.organizedMessageTime!=self.nextMatchMessageTimeStamp() or not oldMessageExists:
            try: #send new message
                channel=self.bot.get_channel(channelID)
                if channel:
                    if self.bot.organizedMessageID is not None:
                        oldMessage=await channel.fetch_message(self.bot.organizedMessageID)
                        await oldMessage.delete()
                    self.bot.organizedMessageTime=self.nextMatchMessageTimeStamp()
                    deep_save_txt(BotPaths.autoOrgTimeStamp_file,str(self.bot.organizedMessageTime))
                    msg=CUSTOM_MATCH_ORGANIZE_MESSAGE.replace("÷",str(self.bot.organizedMessageTime))
                    message=await channel.send(msg)
                    self.bot.organizedMessageID=message.id
                    deep_save_txt(BotPaths.autoOrgID_file,str(self.bot.organizedMessageID))
                    await removeRoleFromEveryone(self.bot,ROLES.CUSTOM_MATCH_PART)
                    printLog("debug","Sent new customs message.")
                    await printLogToDc(self.bot,"debug","Sent new customs message.")
            except Exception as e:
                import traceback
                with open(BotPaths.exception_file, "w") as f:
                    traceback.print_exc(file=f)
                await printLogToDc(self.bot,"error","",BotPaths.exception_file)
        
        # Daily notification at 12:00 UTC
        today=datetime.datetime.now(datetime.timezone.utc).date()
        now_utc=datetime.datetime.now(datetime.timezone.utc)
        
        last_mention_date=self.bot.organizedMessageLastMention

        if now_utc.hour>=12 and last_mention_date!=today.isoformat():
            try:
                mention_channel=await self.bot.fetch_channel(mentionChannelID)
                original_message=await c.fetch_message(self.bot.organizedMessageID)
                
                message_link = original_message.jump_url
                await mention_channel.send(f"{''.join(CUSTOM_MATCH_REMINDER_MESSAGE_BORDER)}{CUSTOM_MATCH_REMINDER_MESSAGE}\n{message_link}{''.join(reversed(CUSTOM_MATCH_REMINDER_MESSAGE_BORDER))}",delete_after=11 * 60 * 60)
                
                deep_save_txt(BotPaths.autoOrgLastMentionDate_file,today.isoformat())
                self.bot.organizedMessageLastMention=today.isoformat()

            except Exception as e:
                import traceback
                with open(BotPaths.exception_file, "w") as f:
                    traceback.print_exc(file=f)
                await printLogToDc(self.bot, "error", "", BotPaths.exception_file)

async def setup(bot):
    await bot.add_cog(AutoOrganizer(bot))
