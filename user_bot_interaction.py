

from discord.ext import commands
import time


from constants import BOT_INTERACTION_TIMEOUT

def checkPastInteractions(data):
  newTimes={}
  for type in data:
    times=[]
    for time in type:
      if int(time)+BOT_INTERACTION_TIMEOUT>time.time():
        times.append(time)
    if len(times)>0:
      newTimes[type]=times
  return newTimes

def interact(bot:commands.Bot,value:float,type:str,id:int):
  userData=bot.user_data
  userData[id]=checkPastInteractions(userData[id])
  if type not in userData[id].keys():
    userData[id][type]=[]
  userData[id][type].append({str(time.time()):value})
  userData["global"][type].append({str(time.time()):value/4})
  bot.user_data=userData

def getInteractValue(bot:commands.Bot,type:str,id:int):
  userData=bot.user_data
  userData[id]=checkPastInteractions(userData[id])
  bot.user_data=userData
  value=0
  for i in userData[id][type]:
    value+=userData[id][type][i]
  return value

def getGlobalInteractValue(bot:commands.Bot,type:str):
  userData=bot.user_data
  userData["global"]=checkPastInteractions(userData["global"])
  bot.user_data=userData
  value=0
  for i in userData["global"][type]:
    value+=userData["global"][type][i]
  return value


