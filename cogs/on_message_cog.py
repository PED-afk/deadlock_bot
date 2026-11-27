


import discord
from discord.ext import commands, tasks

from constants import BOT_SECRET_NICKNAMES
from constants import AUTODELETE_TRESHOLD, MIN_TIME_BETWEEN_SHH_UPDATE_SECONDS
from constants import DEGEN_TIMER_RESET_MESSAGES, DEGEN_TIMER_ASK_MESSAGES, THANKING_MESSAGES
from constants import CHANNEL_IDS

from own_utils import chooseFaceFromCategory
from own_utils import chooseFaceFromCategory, canUseCommand, getShhValue, updateShh
from user_bot_interaction import interact, getGlobalInteractValue, getInteractValue, wasGreeted, botGreets


import random
import time

#on message event

class OnMessage(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.Cog.listener()
    #@bot.event
    async def on_message(self,message):
        #update auto "moderation"
        if self.bot.lastShhCheck+MIN_TIME_BETWEEN_SHH_UPDATE_SECONDS<time.time()//1:
            self.bot.shhMod=updateShh(self.bot.shhMod)
            self.bot.lastShhCheck=time.time()//1
            
        #return if we don't care
        if message.author.bot or message.webhook_id is not None or message.author == self.bot.user:
            return
        
        #if lobby code
        #do fun with it
        if message.channel.id==CHANNEL_IDS.LOBBY_CODES_ID:
            from lobby_code_analizer import isValidCode, analyze_string
            if isValidCode(message.content):
                analized_message=analyze_string(message.content)
                if analized_message is not None:
                    await message.reply(analized_message)
        
        #auto "moderate"
        if getShhValue(message.author.id,self.bot.shhMod)>=AUTODELETE_TRESHOLD:
            await message.delete()
            
        #if someone replied to us check if they thanked us and respond
        idINT=message.author.id
        idSTR=str(idINT)
        if message.reference:
            repliedTo=await message.channel.fetch_message(message.reference.message_id)
            if repliedTo.author.id == self.bot.user.id:
                if any(t in message.content.lower() for t in THANKING_MESSAGES):
                    if any(t in message.content.lower() for t in BOT_SECRET_NICKNAMES):
                        interact(self.bot,3,"thank",idINT)
                        intVal=max(getInteractValue(self.bot,"thank",idINT),getGlobalInteractValue(self.bot,"thank"))
                        if intVal<=10:
                            if "My brain" in repliedTo.content:
                                await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                            else:
                                await message.reply("You're welcome!\n"+chooseFaceFromCategory("spark"))
                        else:
                            await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))
                    else:
                        interact(self.bot,1,"thank",idINT)
                        intVal=max(getInteractValue(self.bot,"thank",idINT),getGlobalInteractValue(self.bot,"thank"))
                        if intVal<=10:
                            if "My brain" in repliedTo.content:
                                await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                            else:
                                await message.reply("You're welcome!\n"+chooseFaceFromCategory("pat"))
                        else:
                            await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))

        #setup user data if the user is not in the "db"
        if str(message.author.id) not in self.bot.user_data.keys():
            self.bot.user_data[idSTR]={}
            self.bot.user_data[idSTR]["main"]="None"
            self.bot.user_data[idSTR]["steamID"]="None"
            self.bot.user_data[idSTR]["steamID3"]="None"
            self.bot.user_data[idSTR]["steamID64"]="None"
            self.bot.user_data[idSTR]["rank"]="None"
            self.bot.user_data[idSTR]["lvl"]=1
            self.bot.user_data[idSTR]["XP"]=0
            self.bot.user_data[idSTR]["wins"]=0
        if "money" not in self.bot.user_data[idSTR].keys():
            self.bot.user_data[idSTR]["money"]={}
            self.bot.user_data[idSTR]["money"]["unsecured"]=0
            self.bot.user_data[idSTR]["money"]["secured"]=0
        if "items" not in self.bot.user_data[idSTR].keys():
            self.bot.user_data[idSTR]["items"]=[]
        if "hidden" not in self.bot.user_data[idSTR].keys():
            self.bot.user_data[idSTR]["hidden"]={}
            self.bot.user_data[idSTR]["hidden"]["messageCD"]=0
            self.bot.user_data[idSTR]["hidden"]["greetMessageCD"]=0
        if "interact" not in self.bot.user_data[idSTR]["hidden"].keys():
            self.bot.user_data[idSTR]["hidden"]["interact"]={}

        #if it's a message with content
        #and user haven't recieved "souls" for talking give them some
        #later "souls" will be used as currency in other functionalities
        if message.content:
            if message.content[0]!="!" and time.time()>=self.bot.user_data[idSTR]["hidden"]["messageCD"]:
                self.bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+self.bot.messageCD
                bonusM=1

                users_in_voice = []

                for guild in self.bot.guilds:
                    for voice_channel in guild.voice_channels:
                        for member in voice_channel.members:
                            users_in_voice.append(str(member.id)+" in "+voice_channel.name)
                if len(users_in_voice)!=0:
                    givesBonus={
                        "good luck":{"bonus":0.5,"alias":{"name":" gl ","bonus":0.25}},
                        "have fun":{"bonus":0.5,"alias":{"name":" hf ","bonus":0.25}},
                    }
                    for i,key in enumerate(givesBonus):
                        if key in message.content:
                            bonusM+=givesBonus[key]["bonus"]
                        elif givesBonus[key]["alias"]["name"] in message.content:
                            bonusM+=givesBonus[key]["alias"]["bonus"]

                lenght=len(message.content)//10
                self.bot.user_data[idSTR]["money"]["unsecured"]+=100+random.randint(0,lenght)*bonusM
                self.bot.user_data[idSTR]["XP"]+=1+random.randint(0,lenght)*bonusM
                level=self.bot.user_data[idSTR]["lvl"]
                if level<self.bot.maxLevel:
                    if self.bot.user_data[idSTR]["XP"]>=100+2**(level/4)+level:
                        self.bot.user_data[idSTR]["XP"]-=100+2**(level/4)+level
                        self.bot.user_data[idSTR]["lvl"]+=1

        #was the bot greeted by a user after a long enough time
        #reply to the greet
        greetAmount=await wasGreeted(message,self.bot.user.id)
        if greetAmount!=0 and time.time()>=self.bot.user_data[idSTR]["hidden"]["greetMessageCD"]:
            self.bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+self.bot.greetCD
            await message.reply(botGreets(greetAmount,message.author.mention))
            return

        #reset the "degen" timer
        #to keep track of time since last "degen" thing said
        if message.content.split(" ")[0].lower() in DEGEN_TIMER_RESET_MESSAGES:
            if len(message.content.split(" "))>=2:
                message.content="!reset_the_timer "+" ".join(message.content.split(" ")[1:])
            else:
                message.content="!reset_the_timer"
            await self.bot.process_commands(message)
            return

        #get the time since last "degen" thing said
        if message.content.lower() in DEGEN_TIMER_ASK_MESSAGES:
            message.content="!the_timer"
            await self.bot.process_commands(message)
            return

        #allow some users to execute multiple commands in 1 message
        if await canUseCommand(message,0,tellReason=False) and message.content.count("!")>1:
            for content in message.content.split("!"):
                if content.strip():
                    message.content="!"+content.strip()
                    await self.bot.process_commands(message)
        else:
            pass
            await self.bot.process_commands(message)
        
        

async def setup(bot):
    await bot.add_cog(OnMessage(bot))