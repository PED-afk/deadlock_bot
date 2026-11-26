


import discord
from discord.ext import commands, tasks

from data_manage import save_json, deep_load_txt, deep_save_txt
from debug import printLog, printLogToDc
from constants import VOICE_CHANNEL_CAT_NAME_PREFIX
from constants import CHANNEL_IDS
from constants import MAX_MONEY_SECURE_AFTER_GAME
from constants import SECOND_BASE
from classes.file_paths import BotPaths

import time
from datetime import datetime, timedelta

import importlib.util
spec = importlib.util.spec_from_file_location("second", SECOND_BASE / "second_main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


#tick event

class TickTick(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.Disabled=True

    @tasks.loop(seconds=1)
    async def tick(self):
        if not self.bot.opSys:
            if module.main({"b":self.bot,"d":"r"})["r"] and not self.Disable:
                module.main({"b":self.bot,"d":"t"})
                if self.bot.tsnskwii==-1:
                    ret=module.main({"s":self.bot.tsnskwii})
                    printLog("info",f"Returned: {ret}")
                    self.bot.tsnskwii=int(deep_load_txt(ret["f"],ret["a"]))
                    if self.bot.tsnskwii==-1:
                        self.bot.tsnskwii=0
                        deep_save_txt(ret["f"],str(self.bot.tsnskwii),ret["a"])
                else:
                    ret=module.main({"s":self.bot.tsnskwii})
                    printLog("info",f"Returned: {ret}")
                    if "act" in ret:
                        for act in ret["act"]:
                            if "c" in act:
                                channel=self.bot.get_channel(CHANNEL_IDS.BOT_DEBUG_CHANNEL)
                                if channel is None:
                                    printLogToDc(self.bot,"error","channel can't be found.")
                                message=await channel.send(".")
                                ctx=await self.bot.get_context(message)
                                await message.delete()
                                await ctx.invoke(self.bot.get_command(act["c"]["n"]),*act["c"]["a"])
                            elif "a" in act:
                                if "bs" in act["a"]:
                                    module.main({"a":self.bot,"d":"i"})
                            
        
        #auto messages
        if len(self.bot.autoMessages)>0:
            now = datetime.now()
            for key, message in self.bot.autoMessages.items():
                if not message["done"]:
                    #find channel
                    here=message["toWhere"]
                    if here=="main":
                        channel=self.bot.get_channel(CHANNEL_IDS.LOUNGE_CHANNEL_ID)
                    elif here=="own":
                        channel=self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID)
                    else:
                        printLog("error",f"Unknown toWhere value: {here}")
                        await printLogToDc(self.bot,"error",f"Unknown toWhere value: {here}")
                        self.bot.autoMessages[key]["done"]=True
                        save_json(BotPaths.autoMessage_file_gitignored,self.bot.autoMessages)
                        continue
                        
                    
                    target_time = datetime.strptime(message["date"],"%Y.%m.%d %H:%M:%S")

                    amount = message["allowedDiference"]["amount"]
                    measurement = message["allowedDiference"]["measurement"].lower()

                    #Convert difference
                    if measurement in ("second", "seconds"):
                        difference=timedelta(seconds=amount)
                    elif measurement in ("minute", "minutes"):
                        difference=timedelta(minutes=amount)
                    elif measurement in ("hour", "hours"):
                        difference=timedelta(hours=amount)
                    elif measurement in ("day", "days"):
                        difference=timedelta(days=amount)
                    elif measurement in ("week", "weeks"):
                        difference=timedelta(weeks=amount)
                    elif measurement in ("year", "years"):
                        #approx: 365 days per year
                        difference=timedelta(days=365*amount)
                    else:
                        printLog("error",f"Unknown measurement: {measurement}")
                        await printLogToDc(self.bot,"error",f"Unknown measurement: {measurement}")
                        self.bot.autoMessages[key]["done"]=True
                        save_json(BotPaths.autoMessage_file_gitignored,self.bot.autoMessages)
                        continue

                    latest_time=target_time+difference

                    if target_time<=now:
                        await printLogToDc(self.bot,"info","Sending auto message.")
                        self.bot.autoMessages[key]["done"]=True
                        if now<=latest_time:
                            await channel.send(key)
                        save_json(BotPaths.autoMessage_file_gitignored,self.bot.autoMessages)
                        
        
        #timers
        for i, (name,timerData) in enumerate(self.bot.timers.items()):
            timerTime=timerData["time"]
            if timerTime!=None:
                if timerData["paused"]:
                    self.bot.timers[name]["time"]+=1
                curTime=time.time()//1
                timerTime=timerTime//1
                if timerTime-curTime==60:
                    await self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).send("1 minute remaining on the "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"] timer.",delete_after=60)
                elif timerTime<=curTime:
                    await self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).send("Moving people in category "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"].",delete_after=60)
                    for guild in self.bot.guilds:
                        category = discord.utils.get(guild.categories, name=VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"]")
                        TARGET=discord.utils.get(category.voice_channels, name="Deadlock ["+name+"]").id
                        SOURCES=[]
                        for other in category.voice_channels:
                            if other.id!=TARGET:
                                SOURCES.append(other.id)
                    allPeople=[]
                    for channel in SOURCES:
                        people=[]
                        lane=self.bot.get_channel(channel)
                        if lane:
                            people=lane.members
                        if len(people)!=0:
                            for member in people:
                                allPeople.append(member.id)
                                try:                                
                                    await member.move_to(self.bot.get_channel(TARGET))
                                except discord.Forbidden:
                                    await self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).send("Can't move "+member.display_name)
                                except discord.HTTPException:
                                    pass
                    if len(allPeople)>=4:
                        for id in allPeople:
                            userID=str(id)
                            if self.bot.user_data[userID]["money"]["unsecured"]>=MAX_MONEY_SECURE_AFTER_GAME:
                                moneyToBeSecured=MAX_MONEY_SECURE_AFTER_GAME
                            else:
                                moneyToBeSecured=self.bot.user_data[userID]["money"]["unsecured"]
                            self.bot.user_data[userID]["money"]["secured"]+=moneyToBeSecured
                            self.bot.user_data[userID]["money"]["unsecured"]-=moneyToBeSecured
                    self.bot.timers[name]["time"]=None
        
        

async def setup(bot):
    await bot.add_cog(TickTick(bot))