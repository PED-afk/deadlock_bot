
import discord
from discord.ext import commands, tasks
import time
from datetime import datetime, timezone, timedelta

from own_utils import chooseFaceFromCategory, canUseCommand, format_duration
from constants import HANDPICKED_SUP_USER_IDS, FUNLOCK_SERVER_ID, BOT_ROLE, ME, MOD_ROLE, MAX_MODERATABLE_MESSAGE_AGE_HOUR, AUTODELETE_TIME_SECONDS
from debug import printLogToDc, printLog
from classes.bot_faces import Faces

#stuff for (semi-)automated moderation

class Mod(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def shh(self,ctx, id=None):
        if await canUseCommand(ctx,3,inChannel=False):
            immune=[self.bot.user.id, ME]
            
            role=ctx.guild.get_role(BOT_ROLE)
            user_ids=[]
            if role:
                user_ids=[member.id for member in role.members]
            immune=immune+user_ids
            role=ctx.guild.get_role(MOD_ROLE)
            user_ids=[]
            if role:
                user_ids=[member.id for member in role.members]
            immune=immune+user_ids
            

            mult=0.5
            if await canUseCommand(ctx,0,tellReason=False):
                mult=4
            elif await canUseCommand(ctx,1,tellReason=False):
                mult=2
            elif await canUseCommand(ctx,2,tellReason=False):
                mult=1
            
            if ctx.message.reference:
                referenced=await ctx.channel.fetch_message(ctx.message.reference.message_id)
                
                age=datetime.now(timezone.utc)-referenced.created_at
                if age>=timedelta(hours=MAX_MODERATABLE_MESSAGE_AGE_HOUR):
                    await ctx.reply(f"You can't `shh` a message older than {MAX_MODERATABLE_MESSAGE_AGE_HOUR} hours.")
                    return
                
                if referenced.author.id in immune:
                    await ctx.reply("You can't moderate this user.")
                    return
                
                if id=="clear":
                    if canUseCommand(ctx,1,False,tellReason=False):
                        self.bot.shhMod[str(referenced.author.id)]=[]
                    else:
                        await ctx.reply("You can't clear users.")
                    return
                
                if str(referenced.author.id) not in self.bot.shhMod:
                    self.bot.shhMod[str(referenced.author.id)]=[]
                if not any(ctx.author.id==entry["user"] for entry in self.bot.shhMod[str(referenced.author.id)]):
                    self.bot.shhMod[str(referenced.author.id)].append({"user":ctx.author.id,"expires":int(time.time())+AUTODELETE_TIME_SECONDS,"mult":mult})
            else:
                if id==None:
                    #guild=self.bot.get_guild(FUNLOCK_SERVER_ID)
                    guild=ctx.guild
                    names=[]
                    for i in HANDPICKED_SUP_USER_IDS:
                        member = guild.get_member(i)
                        if member:
                            names.append("```"+str(i)+"```: "+member.display_name+"\n")
                    await ctx.reply("Please select a user from the hand-picked list, copy their id and use the command again like the following example: `!shh <id>`\n\nOr use the command again as a reply to one of the messages the user sent you want to \"moderate\".\n"+"\n".join(names))
                elif id.isnumeric():
                    if id in immune:
                        await ctx.reply("You can't moderate this user.")
                        return
                    
                    if str(id) not in self.bot.shhMod:
                        self.bot.shhMod[str(id)]=[]
                    if not any(ctx.author.id==entry["user"] for entry in self.bot.shhMod[str(id)]):
                        self.bot.shhMod[str(id)].append({"user":ctx.author.id,"expires":int(time.time())+AUTODELETE_TIME_SECONDS,"mult":mult})
                else:
                    await ctx.reply("Can not interpret ID.\n-# Maybe you provided a name instead of an ID."+chooseFaceFromCategory(Faces.wink))

async def setup(bot):
    await bot.add_cog(Mod(bot))
