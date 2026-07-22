
import random
from discord.ext import commands

from dc_ids import ME, BOT_ROLE, BOTS_CHANNEL_ID

def chooseFaceFromCategory(bot,category:str):
    if category in bot.faces:
        faces=bot.faces[category]
    else:
        faces=["(face category not found)"]
    r=random.randint(0,len(faces)-1)
    return faces[r]

def activeTimerExists(bot:commands.Bot):
    for i, (timerName,timerData) in enumerate(bot.timers.items()):
        if timerData["time"]!=None:
            return True
    return False

async def canUseCommand(ctx:commands.Context, level:int=2, inVoice:bool=False):
    """
    
    Check if user can use this command\n
    <level>\n
    0: user id must match ME (and must be in the correct channel)\n
    1: must have the "can use the bot" role (and must be in the correct channel)\n
    2: just check for correct channel\n\n
    \n
    <inVoice>\n
    If True, user must be in a voice channel
    """
    
    if ctx.channel.id!=BOTS_CHANNEL_ID:
        return False

    if level==0 and ctx.author.id!=ME:
        await ctx.reply("You do not have permission to use this command.")
        return False
    elif level==1 and not any(role.id==BOT_ROLE for role in ctx.author.roles):
        await ctx.reply("You do not have permission to use this command.")
        return False

    if inVoice and ctx.author.voice==None:
        await ctx.reply("You must be in a voice channel to use this command.")
        return False

    return True