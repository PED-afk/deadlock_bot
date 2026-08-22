

from discord.ext import commands
import time


from constants import BOT_INTERACTION_TIMEOUT
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


def botWasGreeted(message:str):
  acceptPrefix=[]
  greet=[]
  
  return False

async def botGreets():
  return ""




