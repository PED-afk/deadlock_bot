

from discord.ext import commands
import time


from constants import BOT_INTERACTION_TIMEOUT

def checkPastInteractions(data):
  newTimes={}
  for type in data:
    times=[]
    for time in type:
      if time+BOT_INTERACTION_TIMEOUT>time.time():
        times.append(time)
    if len(times)>0:
      newTimes[type]=times
  return newTimes

def interact(bot:commands.Bot,value:int,type:str,id:int):
  userData=bot.user_data
  userData[id]=checkPastInteractions(userData[id])
  if type not in userData[id].keys():
    userData[id][type]=[]
  for i in range(value):
    UserData[id][type].append(time.time())
  bot.user_data=userData

def getInteractValue(bot:commands.Bot,type:str,id:int):
  userData[id]=checkPastInteractions(userData[id])
  bot.user_data=userData
  return len(userData[id][type])




