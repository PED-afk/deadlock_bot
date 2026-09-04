
import random
from discord.ext import commands
from datetime import datetime

from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID
from debug import printLog
from classes.bot_faces import Faces

BOTFACES=Faces

def chooseFaceFromCategory(category:str|list[str]) -> str:
    """
    
    Randomly selects a face from the given category
    """
    if isinstance(category,list):
        category=random.choice(category)
    if category not in BOTFACES.faces:
        return f"(face category {category} not found)"
    curFaces=BOTFACES.faces[category]
    return random.choice(curFaces)

def activeTimerExists(bot:commands.Bot):
    """
    Returns True if the bot arg has any timers that are not `None`
    """
    for i, (timerName,timerData) in enumerate(bot.timers.items()):
        if timerData["time"]!=None:
            return True
    return False

async def canUseCommand(ctx:commands.Context, level:int=2, inVoice:bool=False, tellReason:bool=True):
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

    #if ctx.channel.id!=BOTS_CHANNEL_ID:
        #return False

    if level==0 and ctx.author.id!=ME:
        if tellReason:
            await ctx.reply("You are not the main guy.")
        return False
    elif level==1 and not any(role.id==BOT_ROLE for role in ctx.author.roles):
        if tellReason:
            await ctx.reply("You do not have permission to use this command.")
        return False

    if inVoice and ctx.author.voice==None:
        if tellReason:
            await ctx.reply("You must be in a voice channel to use this command.")
        return False

    return True

async def getDictStr(d: dict, hideSome:bool=False, hideThese:dict={"hidden":"normal","items":"len=#0","steamID3":"normal","steamID64":"normal","rank":"value=#None"}, format:bool=True, indent=0):
    """

    Creates a str from a dict <key>:<value> format\n\n
    hideSome: skips specific keys specified in hideThese\n
    hideThese: a dict containing the keys to hide and when to hide them.

    """
    inData=""
    for innerKey, innerData in d.items():
        if hideSome:
            for i,(key,data) in enumerate(hideThese.items()):
                if innerKey==key:
                    if data=="normal":
                        continue
                    if "len" in data:
                        inDataLen=len(innerData)
                        if "!=" in data:
                            if inDataLen!=int(data.split("#")[1]):
                                continue
                        if "=" in data:
                            if inDataLen==int(data.split("#")[1]):
                                continue
                        if ">" in data:
                            if inDataLen>int(data.split("#")[1]):
                                continue
                        if "<" in data:
                            if inDataLen<int(data.split("#")[1]):
                                continue
                    if "value" in data:
                        inDataLen=len(innerData)
                        if "!=" in data:
                            if inDataLen!=data.split("#")[1]:
                                continue
                        if "=" in data:
                            if inDataLen==data.split("#")[1]:
                                continue
                        if ">" in data:
                            if inDataLen>data.split("#")[1]:
                                continue
                        if "<" in data:
                            if inDataLen<data.split("#")[1]:
                                continue
        if indent==0:
            if format:
                inData+="# "
        if isinstance(innerData, dict):
            inData+="\t"*indent+str(innerKey)+":\n"
            inData+="\t"*indent+await getDictStr(innerData, hideSome, hideThese, format, indent+1)
        else:
            inData+="\t"*indent+str(innerKey)+":\n"+str(innerData)+"\n"
    return inData

def format_duration(seconds: int) -> str:
    """
    Turns a second interval into year month etc format leaving out leading zeros.\nReturns a str
    """
    units=[
        ("year", 365 * 24 * 60 * 60),
        ("month", 30 * 24 * 60 * 60),
        ("day", 24 * 60 * 60),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]
    parts=[]
    for name, size in units:
        value, seconds=divmod(seconds, size)
        # Don't show leading zeros
        if value or parts:
            parts.append(f"{value} {name}{'s' if value!=1 else ''}")
    return ", ".join(parts)

def formatedCurTime():
    """
    Returns the current time in Year-Month-Day Hour:Minute:Second format
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
