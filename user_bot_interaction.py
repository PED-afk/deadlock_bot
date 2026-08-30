

from discord.ext import commands
import time
import random

from constants import BOT_INTERACTION_TIMEOUT, ACCEPTED_GREETS, GREET_RESPONSES, GREET_SEARCH_LIMIT, BOT_SECRET_NICKNAMES
from own_utils import chooseFaceFromCategory
from debug import printLog

def checkPastInteractions(data):
    newTimes={}
    for type in data:
        times=[]
        for iTime in data[type]:
            if int(data[type][iTime])+BOT_INTERACTION_TIMEOUT>time.time():
                times.append(data[type][iTime])
        if len(times)>0:
            newTimes[type]=times
    return newTimes

def interact(bot:commands.Bot,value:float,type:str,id:int):
    userData=bot.user_data
    id=str(id)
    userData[id]["hidden"]["interact"]=checkPastInteractions(userData[id]["hidden"]["interact"])
    userData["global"]["hidden"]["interact"]=checkPastInteractions(userData["global"]["hidden"]["interact"])

    if type not in userData[id]["hidden"]["interact"].keys():
        userData[id]["hidden"]["interact"][type]={}
    userData[id]["hidden"]["interact"][type][str(time.time())]=value

    if type not in userData["global"]["hidden"]["interact"].keys():
        userData["global"]["hidden"]["interact"][type]={}
    userData["global"]["hidden"]["interact"][type][str(time.time())]=value/4

    bot.user_data=userData

def getInteractValue(bot:commands.Bot,type:str,id:int):
    userData=bot.user_data
    id=str(id)
    userData[id]["hidden"]["interact"]=checkPastInteractions(userData[id]["hidden"]["interact"])
    bot.user_data=userData
    if type not in userData[id]["hidden"]["interact"].keys():
        return 0
    value=0
    for i in userData[id]["hidden"]["interact"][type]:
        value+=userData[id]["hidden"]["interact"][type][i]
    return value

def getGlobalInteractValue(bot:commands.Bot,type:str):
    userData=bot.user_data
    userData["global"]["hidden"]["interact"]=checkPastInteractions(userData["global"]["hidden"]["interact"])
    bot.user_data=userData
    if type not in userData["global"]["hidden"]["interact"].keys():
        return 0
    value=0
    for i in userData["global"]["hidden"]["interact"][type]:
        value+=userData["global"]["hidden"]["interact"][type][i]
    return value


async def wasGreeted(message,id) -> int:
    wasReference=(message.reference and await message.channel.fetch_message(message.reference.message_id).author.id==id)
    if wasReference:
        previous_message=message.channel.fetch_message(message.reference.message_id).content.lower()
    else:
        return 0
        #return for now
        #idk if I want to create an alg to decide if a greet message was for the bot or someone else
        async for msg in message.channel.history(limit=GREET_SEARCH_LIMIT, before=message):
            previous_message=msg.content
            printLog("info",previous_message)
    if previous_message in ACCEPTED_GREETS:
        if any(i in previous_message for i in BOT_SECRET_NICKNAMES):
            return 2
        else:
            return 1
    return 0

async def botGreets(greetAmount:int) -> str:
    resp=GREET_RESPONSES[random.randint(0,len(GREET_RESPONSES)-1)]
    if greetAmount==1:
        face=chooseFaceFromCategory(["happy"])
    else:
        face=chooseFaceFromCategory(["love","blush_happy","pat","spark","excited"])
    return ""




