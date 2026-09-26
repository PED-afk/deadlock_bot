

import discord
from discord.ext import commands, tasks

import os
from dotenv import load_dotenv
import time
import random

from data_manage import save_json, load_json, load_txt, deep_load_json, deep_load_txt
"""
load_txt returns a list of str from the filepath
load_json and save_json loads from and saves to json files

neither does anything else other than open the file on the filepath and load the data from it
"""
from own_utils import chooseFaceFromCategory, canUseCommand, getShhValue, updateShh
from debug import printLog, printLogToDc
from constants import BOTS_CHANNEL_ID, MESSAGE_CD, VOICE_CHANNEL_CAT_NAME_PREFIX, BOT_SECRET_NICKNAMES, GREET_CD
from constants import ROLE_CHANNEL_ID, WHO_AM_I_ROLES, COLOR_CHOOSER_MESSAGE_ID, IAM_MESSAGE_ID, IAM_MESSAGE_CONTENT, COLOR_CHOOSER_MESSAGE_CONTENT, COLORED_ROLES
from constants import AUTODELETE_TRESHOLD, MIN_TIME_BETWEEN_SHH_UPDATE_SECONDS
from constants import DEGEN_TIMER_RESET_MESSAGES, DEGEN_TIMER_ASK_MESSAGES, THANKING_MESSAGES
from constants import WARNING_MESSAGE_IN_NAMETAG_CHANNEL_ID, WARNING_MESSAGE_IN_NAMETAG_CHANNEL
from constants import ROLES

from classes.item import Item
from classes.file_paths import BotPaths
from user_bot_interaction import interact, getGlobalInteractValue, getInteractValue, wasGreeted, botGreets


#Set up the bot with a command prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.voice_states = True

intents.reactions = True
intents.members = True
intents.guilds = True

intents.presences = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.hiddens")
        await self.load_extension("cogs.timer")
        await self.load_extension("cogs.power")
        await self.load_extension("cogs.unorganized")
        await self.load_extension("cogs.debug_cog")
        await self.load_extension("cogs.moderator")
        await self.load_extension("cogs.tools")
        await self.load_extension("cogs.spok_cog")
        await self.load_extension("cogs.thread_cog")
        await self.load_extension("cogs.reactions_cog")
        #await self.load_extension("cogs.priority_cog")

#bot=commands.Bot(command_prefix='!', intents=intents)
#this does NOT work with cogs for some reason

bot=MyBot(command_prefix='!', intents=intents)

def loadItemsProper(items):
    newItems=[]
    for curItem in items:
        curItemParts=curItem.split(" ")
        newItems.append(Item(curItemParts[0],int(curItemParts[1]),curItemParts[2]))
    return newItems


@bot.event
async def on_ready():
    guild=bot.get_guild(123456789012345678)
    if guild:
        await guild.me.edit(nick=bot.name)

    pfp_files=list(BotPaths.pfp_folder.glob("*.jpg"))
    if pfp_files:
        pfp_path=random.choice(pfp_files)
        printLog("info",f"Chosen pfp: {pfp_path}")
        with pfp_path.open("rb") as f:
            await bot.user.edit(avatar=f.read())
        printLog("info",f"Changed PFP to {pfp_path.name}")
    else:
        printLog("error",f"No .jpg files found in {BotPaths.pfp_folder}")


    printLog("info",f"Bot connected as {bot.user}")

    guild = bot.get_channel(BOTS_CHANNEL_ID).guild
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    
    face=chooseFaceFromCategory("big_eyes")

    with open(BotPaths.hotboot_file,"r") as f:
        if int(f.readline().strip())==0:
            await bot.get_channel(BOTS_CHANNEL_ID).send("I'm awake!\nGood morning!\n"+face)
        else:
            await bot.get_channel(BOTS_CHANNEL_ID).send("Back online! "+face)

    tempData=load_txt(BotPaths.update_check_file)
    if len(tempData)!=0:
        printLogToDc(bot,"info",tempData[0])


    #edit the role select messages
    channel=bot.get_channel(ROLE_CHANNEL_ID)
    message=await channel.fetch_message(COLOR_CHOOSER_MESSAGE_ID)
    await message.edit(content=COLOR_CHOOSER_MESSAGE_CONTENT)
    for i in COLORED_ROLES:
        await message.add_reaction(COLORED_ROLES[i]["emoji"])

    message=await channel.fetch_message(IAM_MESSAGE_ID)
    await message.edit(content=IAM_MESSAGE_CONTENT)
    for i in WHO_AM_I_ROLES:
        await message.add_reaction(WHO_AM_I_ROLES[i]["emoji"])

    message=await channel.fetch_message(WARNING_MESSAGE_IN_NAMETAG_CHANNEL_ID)
    await message.edit(content=WARNING_MESSAGE_IN_NAMETAG_CHANNEL.replace("@",bot.user.mention).replace(" #",bot.get_channel(BOTS_CHANNEL_ID).mention))


    #need a message in a channel? use this:
    
    """
    channel=bot.get_channel(ROLE_CHANNEL_ID)
    if channel is None:
        channel=await bot.fetch_channel(ROLE_CHANNEL_ID)
    await channel.send("New message!")
    exit()
    """

    #thess were needed once
    """
    forum = bot.get_channel(1544085021156184214)

    if not isinstance(forum, discord.ForumChannel):
        raise ValueError("The specified channel is not a forum channel.")

    existing = {tag.name for tag in forum.available_tags}

    for name in ["Tank","Support","Spirit Carry","Gun Carry","Spirit focus","Gun focus","Vitality focus","Lane bully","Assasin","Controll"]:
        if name in existing:
            continue

        await forum.create_tag(name=name)
    """

    

    if not tick.is_running():
        tick.start()

@bot.event
async def on_message(message):
    if bot.lastShhCheck+MIN_TIME_BETWEEN_SHH_UPDATE_SECONDS<time.time()//1:
        bot.shhMod=updateShh(bot.shhMod)
        bot.lastShhCheck=time.time()//1
        
    if message.author.bot or message.webhook_id is not None or message.author == bot.user:
        return
    
    if getShhValue(message.author.id,bot.shhMod)>=AUTODELETE_TRESHOLD:
        await message.delete()
        
    
    idINT=message.author.id
    idSTR=str(idINT)
    if message.reference:
        repliedTo=await message.channel.fetch_message(message.reference.message_id)
        if repliedTo.author.id == bot.user.id:
            if any(t in message.content.lower() for t in THANKING_MESSAGES):
                if any(t in message.content.lower() for t in BOT_SECRET_NICKNAMES):
                    interact(bot,3,"thank",idINT)
                    intVal=max(getInteractValue(bot,"thank",idINT),getGlobalInteractValue(bot,"thank"))
                    if intVal<=10:
                        if "My brain" in repliedTo.content:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                        else:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("spark"))
                    else:
                        await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))
                else:
                    interact(bot,1,"thank",idINT)
                    intVal=max(getInteractValue(bot,"thank",idINT),getGlobalInteractValue(bot,"thank"))
                    if intVal<=10:
                        if "My brain" in repliedTo.content:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                        else:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("pat"))
                    else:
                        await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))


    if str(message.author.id) not in bot.user_data.keys():
        bot.user_data[idSTR]={}
        bot.user_data[idSTR]["main"]="None"
        bot.user_data[idSTR]["steamID"]="None"
        bot.user_data[idSTR]["steamID3"]="None"
        bot.user_data[idSTR]["steamID64"]="None"
        bot.user_data[idSTR]["rank"]="None"
        bot.user_data[idSTR]["lvl"]=1
        bot.user_data[idSTR]["XP"]=0
        bot.user_data[idSTR]["wins"]=0
    if "money" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["money"]={}
        bot.user_data[idSTR]["money"]["unsecured"]=0
        bot.user_data[idSTR]["money"]["secured"]=0
    if "items" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["items"]=[]
    if "hidden" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["hidden"]={}
        bot.user_data[idSTR]["hidden"]["messageCD"]=0
        bot.user_data[idSTR]["hidden"]["greetMessageCD"]=0
    if "interact" not in bot.user_data[idSTR]["hidden"].keys():
        bot.user_data[idSTR]["hidden"]["interact"]={}


    if message.content:
        if message.content[0]!="!" and time.time()>=bot.user_data[idSTR]["hidden"]["messageCD"]:
            bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+bot.messageCD
            bonusM=1

            users_in_voice = []

            for guild in bot.guilds:
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
            bot.user_data[idSTR]["money"]["unsecured"]+=100+random.randint(0,lenght)*bonusM
            bot.user_data[idSTR]["XP"]+=1+random.randint(0,lenght)*bonusM
            level=bot.user_data[idSTR]["lvl"]
            if level<bot.maxLevel:
                if bot.user_data[idSTR]["XP"]>=100+2**(level/4)+level:
                    bot.user_data[idSTR]["XP"]-=100+2**(level/4)+level
                    bot.user_data[idSTR]["lvl"]+=1

    greetAmount=await wasGreeted(message,bot.user.id)
    if greetAmount!=0 and time.time()>=bot.user_data[idSTR]["hidden"]["greetMessageCD"]:
        bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+bot.greetCD
        await message.reply(botGreets(greetAmount,message.author.mention))
        return


    if message.content.lower() in DEGEN_TIMER_RESET_MESSAGES:
        message.content = "!reset_the_timer"
        await bot.process_commands(message)
        return

    if message.content.lower() in DEGEN_TIMER_ASK_MESSAGES:
        message.content = "!the_timer"
        await bot.process_commands(message)
        return

    if await canUseCommand(message,0,tellReason=False) and message.content.count("!")>1:
        for content in message.content.split("!"):
            if content.strip():
                message.content="!"+content.strip()
                await bot.process_commands(message)
    else:
        await bot.process_commands(message)


@tasks.loop(seconds=1)
async def tick():
    for i, (name,timerData) in enumerate(bot.timers.items()):
        timerTime=timerData["time"]
        if timerTime!=None:
            if timerData["paused"]:
                bot.timers[name]["time"]+=1
            curTime=time.time()//1
            timerTime=timerTime//1
            if timerTime-curTime==60:
                await bot.get_channel(BOTS_CHANNEL_ID).send("1 minute remaining on the "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"] timer.",delete_after=60)
            elif timerTime<=curTime:
                await bot.get_channel(BOTS_CHANNEL_ID).send("Moving people in category "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"].",delete_after=60)
                for guild in bot.guilds:
                    category = discord.utils.get(guild.categories, name=VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"]")
                    TARGET=discord.utils.get(category.voice_channels, name="Deadlock ["+name+"]").id
                    SOURCES=[]
                    for other in category.voice_channels:
                        if other.id!=TARGET:
                            SOURCES.append(other.id)
                for channel in SOURCES:
                    people=[]
                    lane=bot.get_channel(channel)
                    if lane:
                        people=lane.members
                    if len(people)!=0:
                        for member in people:
                            try:
                                await member.move_to(bot.get_channel(TARGET))
                            except discord.Forbidden:
                                await bot.get_channel(BOTS_CHANNEL_ID).send("Can't move "+member.display_name)
                            except discord.HTTPException:
                                pass
                bot.timers[name]["time"]=None


bot.startTimers={"A":11*60,"B":11*60}
bot.timers={"A":{"time":None,"paused":False},"B":{"time":None,"paused":False}}

bot.shhMod={}
bot.lastShhCheck=time.time()//1


bot.bootTime=time.time()//1
bot.version="0.10.0"
bot.versionSTR="Cleaning and documentation start"

bot.name="FUNLOCK BOT" #Not yet decided



bot.messageCD=MESSAGE_CD
bot.greetCD=GREET_CD
bot.degenTimer=int(float(deep_load_txt(BotPaths.degen_timer_file)))

bot.user_data=deep_load_json(BotPaths.user_data_file)
idSTR="global"
if idSTR not in bot.user_data.keys():
    bot.user_data[idSTR]={}
    bot.user_data[idSTR]["main"]="None"
    bot.user_data[idSTR]["steamID"]="None"
    bot.user_data[idSTR]["steamID3"]="None"
    bot.user_data[idSTR]["steamID64"]="None"
    bot.user_data[idSTR]["rank"]="None"
    bot.user_data[idSTR]["lvl"]=1
    bot.user_data[idSTR]["XP"]=0
    bot.user_data[idSTR]["wins"]=0
if "money" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["money"]={}
    bot.user_data[idSTR]["money"]["unsecured"]=0
    bot.user_data[idSTR]["money"]["secured"]=0
if "items" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["items"]=[]
if "hidden" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["hidden"]={}
    bot.user_data[idSTR]["hidden"]["messageCD"]=0
    bot.user_data[idSTR]["hidden"]["greetMessageCD"]=0
if "interact" not in bot.user_data[idSTR]["hidden"].keys():
    bot.user_data[idSTR]["hidden"]["interact"]={}

bot.characters=load_txt(BotPaths.characters_file)
bot.characters=load_json(BotPaths.characters_file_json)
bot.maxLevel=bot.characters[list(bot.characters.keys())[0]]["maxLvl"]

bot.items=loadItemsProper(load_txt(BotPaths.items_file))
bot.map_graph=load_json(BotPaths.map_graph_file)

bot.ranks=load_json(BotPaths.ranks_file)

load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))



