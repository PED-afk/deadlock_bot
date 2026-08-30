

from discord.ext import commands
import time
import random

from constants import BOT_INTERACTION_TIMEOUT, ACCEPTED_GREETS, GREET_RESPONSES, GREET_SEARCH_LIMIT, BOT_SECRET_NICKNAMES
from own_utils import chooseFaceFromCategory
from debug import printLog
from classes.bot_faces import Faces

def checkPastInteractions(data:dict) -> dict:
    newTimes={}
    for interact_type in data:
        times={}
        for iTime,value in data[interact_type].items():
            if int(iTime)+BOT_INTERACTION_TIMEOUT>time.time():
                times[iTime]=value
        if times:
            newTimes[interact_type]=times
    return newTimes

def interact(bot:commands.Bot,value:float,interact_type:str,userID:int):
    userData=bot.user_data
    userID=str(userID)
    userData[userID]["hidden"]["interact"]=checkPastInteractions(userData[userID]["hidden"]["interact"])
    userData["global"]["hidden"]["interact"]=checkPastInteractions(userData["global"]["hidden"]["interact"])

    curTime=str(int(time.time()))

    if interact_type not in userData[userID]["hidden"]["interact"]:
        userData[userID]["hidden"]["interact"][interact_type]={}
    userData[userID]["hidden"]["interact"][interact_type][curTime]=value

    if interact_type not in userData["global"]["hidden"]["interact"]:
        userData["global"]["hidden"]["interact"][interact_type]={}
    userData["global"]["hidden"]["interact"][interact_type][curTime]=value/4

    bot.user_data=userData

def getInteractValue(bot:commands.Bot,interact_type:str,userID:int) -> int:
    userData=bot.user_data
    userID=str(userID)
    userData[userID]["hidden"]["interact"]=checkPastInteractions(userData[userID]["hidden"]["interact"])
    bot.user_data=userData
    if interact_type not in userData[userID]["hidden"]["interact"]:
        return 0
    value=0
    for i in userData[userID]["hidden"]["interact"][interact_type]:
        value+=userData[userID]["hidden"]["interact"][interact_type][i]
    return value

def getGlobalInteractValue(bot:commands.Bot,interact_type:str) -> int:
    userData=bot.user_data
    userData["global"]["hidden"]["interact"]=checkPastInteractions(userData["global"]["hidden"]["interact"])
    bot.user_data=userData
    if interact_type not in userData["global"]["hidden"]["interact"]:
        return 0
    value=0
    for i in userData["global"]["hidden"]["interact"][interact_type]:
        value+=userData["global"]["hidden"]["interact"][interact_type][i]
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
    #if any(i in ACCEPTED_GREETS for i in previous_message.split(" ")):
    #dont use
    #message can contain stuff we check for but is not a great
    #this is important to when we check for not referenced images
    if " ".join(i.removesuffix("!") for i in previous_message.split(" ")[:-2]).lower() in ACCEPTED_GREETS: #this checks for if the message is: [greet] [secret name (optional)]
        if any(i in previous_message for i in BOT_SECRET_NICKNAMES):
            return 2
        else:
            return 1
    return 0

async def botGreets(greetAmount:int, mention:str) -> str:
    resp=GREET_RESPONSES[random.randint(0,len(GREET_RESPONSES)-1)]
    if greetAmount==1:
        face=chooseFaceFromCategory(Faces.happy)
    else:
        face=chooseFaceFromCategory(Faces.FaceBigCategory.happies)
    ping_user=""
    if random.randint(0,3)==0:
        ping_user=" "+mention
    return resp+ping_user+" :wave:"+face




