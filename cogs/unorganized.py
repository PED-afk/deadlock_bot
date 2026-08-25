
import discord
from discord.ext import commands, tasks
import time
import platform
from pathlib import Path
import random

from own_utils import chooseFaceFromCategory, activeTimerExists, canUseCommand, getDictStr
from data_manage import save_json, load_json, load_txt
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID
from pi_specific import getAll
from debug import printLog, printLogToDc
from data_manage import load_json

from classes.button import Button, MultButton
from classes.find_rem import FindRem
from classes.run_home import runHome
from classes.file_paths import BotPaths


#there should be no commands here

#this exists because I wanted to quickly move
#all commands from the main bot file to cogs

#these commands should be organized into their own cogs later

class Unorganized(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def test(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id == BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                await ctx.send("TEST:\nNothing to test.\n.=.",delete_after=10)
                view=Button()
                view=MultButton(ctx.author)
                view=FindRem(ctx,self.bot)
                await ctx.send("Buttons:", view=view)

    @commands.command()
    async def minigames(self, ctx, game:str=None):
        senderID=ctx.author.id
        if ctx.channel.id == BOTS_CHANNEL_ID:
            if game==None:
                games=[
                    "`!minigames find_Rem`: Try to find the enemy Rem and stop them from getting the sinners.",
                    "`!minigames run_home`: Try to go back to your base to secure your unsecured souls. (can only use if you have unsecured souls: `!my_data`)"
                ]
                await ctx.reply('\n'.join(games))
            elif game=="find_Rem":
                view=FindRem(ctx,self.bot)
                print(view.buttonTexts)
                await ctx.reply("Find the enemy Rem:", view=view)
            elif game=="run_home_not_done":
                if self.bot.user_data[str(senderID)]["main"]=="None":
                    await ctx.reply("You need to set a main first using `!set_main` in order to play this minigame")
                else:
                    userData={
                        "maxHP":self.bot.characters[self.bot.user_data[str(senderID)]["main"]]["base_HP"]+self.bot.user_data[str(senderID)]["lvl"]*self.bot.characters[self.bot.user_data[str(senderID)]["main"]]["perLvl"],
                        "HP":self.bot.characters[self.bot.user_data[str(senderID)]["main"]]["base_HP"]+self.bot.user_data[str(senderID)]["lvl"]*self.bot.characters[self.bot.user_data[str(senderID)]["main"]]["perLvl"],
                        "Lvl":self.bot.user_data[str(senderID)]["lvl"],
                        "main":self.bot.user_data[str(senderID)]["main"]
                    }
                    view=runHome(ctx,"before start",userData,self.bot)
                    await ctx.reply("Get back to the base!\nYou have: "+str(self.bot.user_data[str(senderID)]["money"]["unsecured"])+" unsecured souls!", view=view)
            else:
                await ctx.reply("No minigame exists with that name."+chooseFaceFromCategory(self.bot,"nervous"))


    @commands.command()
    async def help_me(self, ctx, section:str=None):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            anyView=True
            if section==None:
                anyView=True
                botcommands=[
                    "`!help timer`: Commands about my timer functionality.",
                    "`!help voice`: Commands about me using voice channels.",
                    "`!help admin`: Commands that only 'important' people can use.",
                    "`!help data`: Commands about a minigame that is in development.",
                    "`!help tools`: Commands about some 'tools' and tools I can provide to spice up your game.",
                    "`!help extra`: Commands about no particular topic.",
                ]
            elif section=="timer":
                anyView=True
                botcommands=[
                    "`!start` and `!start second`: Start an x minute timer. When the timer ends I put everyone into the `Deadlock [#]` channel (from lane channels).\n(Timer lenght is configureable; only 1 timer can be used at the same time (as right no there is only 1 set of lane channels))",
                    "`!end`: Ends the timer and moves everyone immediately.",
                    "`!endit`: Ends the timer without sending people to the `Deadlock [#]` channel.",
                    "`!settimer x`: Set the timer lenght to x minutes.",
                    "`!gettimer`: Tells you the timer lenght.",
                    "`!remaining:` Tells you how much time remains on the timer.",
                ]
            elif section=="voice":
                face=chooseFaceFromCategory(self.bot,"annoyed")
                anyView=True
                botcommands=[
                    "`!join`: I will join `Deadlock [#]` and will use an experimental feature to automate my timer functionality.",
                    "`!leave`: I will leave `Deadlock [#]` but will contionue counting for the timer.",
                    "(feature is not possible "+face+", but I can be there for emotional support."
                ]
            elif section=="admin":
                anyView=False
                botcommands=[
                    "`!ping`: I will send 'Pong!' if I'm alive.",
                    "`!status`: My version, OS and hardware I run on.",
                    "`!check_cogs`: Check if a cog is loaded.",
                    "`!get_logs`: I send you certain logs.",
                    "`!sleep`: I will sleep until a certain hour to save on energy and hardware integrity. (the bot is unavailable during sleep but will automatically start at* the designated hour)"
                    "`!restart:` or `!reload`: I will restart and apply changes to my code.",
                    "`!clear_loaded`: I forget stuff so I don't save incorrect data.",
                    "`!clear_user_data`: Clears user_data.json",
                    "`!shutdown`: This kills me :("
                ]
            elif section=="data":
                anyView=True
                botcommands=[
                    "Some data collection for now, maybe roles or nicknames later?\n(Also steamid for lane assign logic if there ever be a way for it.)",
                    "`!set_main`: Set this to your most played character so others can know.",
                    "`!set_steam_id <steamid64>`: Add your Steam ID64 — your rank will be fetched automatically from the Deadlock API and your Discord role will be assigned.",
                    "`!update_rank`: Refresh your rank from the Deadlock API (use after ranking up/down).",
                    "`!set_rank`: Manually set your rank if the API can't fetch it.",
                    "`!my_data`: I will tell you what data I have on you.",
                    "`!remove_me`: I will remove your data from the \"database\"",
                    "`!save`: Save from variable to a file. (will save automaticaly on shutdown and restart)",
                ]
            elif section=="extra":
                anyView=True
                botcommands=[
                    "`!minigame`: Play some games while you wait for matchmaking.",
                    "`!source`: Lobotomy (source code).",
                    "`!credit`: Give credit to people we use the works of."
                ]
            elif section=="tools":
                anyView=True
                botcommands=[
                    "`!rand X Y`: All sorts of randomly given stuff. (use `!rand` to learn more)",
                    "`!people_at_rank <rank> <radius> <online>`: Give you the names of people who have ranks around `<rank>`(±`<radius>` (if present)). If `<online>` is present and is set to `1`, will only search from people currently online. If `<rank>` is omited I will use your rank as base."
                ]
            else:
                await ctx.reply("No command 'folder' exist with that name.")
                return

            if (senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles)) or anyView:
                if len(botcommands)!=0:
                    await ctx.reply('\n'.join(botcommands))

    @commands.command()
    async def status(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if random.randint(0,9)==0:
                if senderID==ME:
                    face=chooseFaceFromCategory(self.bot,"annoyed")
                    #WATCH OUT!!!
                    #DO NOT DELETE OR REPLACE
                    l="‎ " #this is not a 'space' character (that wouldn't work) this is an invisible character different from a 'space'
                    #DO NOT DELETE OR REPLACE
                    #WATCH OUT!!!
                    for i in face:
                        l+=" "
                    l+="(Why do you want to know?)"
                    await ctx.reply(l+"\n"+face)
            winlin=platform.system()
            cpu=platform.machine()
            try:
                lindistr=platform.freedesktop_os_release()
            except:
                lindistr=None
            curTime=time.time()//1
            diff=curTime-self.bot.bootTime
            hours=diff//60//60
            diff-=diff//60//60*60*60
            minutes=diff//60
            diff-=diff//60*60
            seconds=diff
            extra=""
            if hours>24:
                extra="\nI'm tired. "+chooseFaceFromCategory(self.bot,"tired")
            await ctx.reply("Bot version: "+self.bot.version+" "+self.bot.versionSTR+"\nOS: "+winlin+"\nHardware I'm living on: "+cpu+"\nI've been running for: "+str(hours)+" hours, "+str(minutes)+" minutes and "+str(seconds)+" seconds."+extra)
            if lindistr!=None:
                await ctx.reply(getAll()+lindistr["PRETTY_NAME"],delete_after=30)
                #await ctx.send("Fun fact: Most likely I'm running on a rasberry pi 5. :D\nLinux dist: "+lindistr["PRETTY_NAME"],delete_after=30)

    @commands.command()
    async def version(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            await ctx.reply("Bot version: "+self.bot.version+" "+self.bot.versionSTR)

    @commands.command()
    async def join(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.guild.voice_client!=None:
                    await ctx.reply("Sorry I'm busy in another channel. "+chooseFaceFromCategory(self.bot,"nervous"))
                else:
                    if ctx.author.voice==None:
                        await ctx.reply("You must be in a voice channel so I know which channel to join.")
                    else:
                        channel = ctx.author.voice.channel
                        await channel.connect()

    @commands.command()
    async def leave(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                if ctx.voice_client:
                    if ctx.author.voice==None:
                        await ctx.reply("You must be in a voice channel so I know if you are allowed to make me leave.")
                    else:
                        if ctx.author.voice.channel == ctx.voice_client.channel:
                            await ctx.guild.voice_client.disconnect()
                else:
                    await ctx.reply("I'm not in any voice channels.")

    @commands.command()
    async def source(self,ctx):
        if await canUseCommand(ctx,2):
            file=discord.File(Path(__file__))
            await ctx.reply("My brain: `https://github.com/PED-afk/deadlock_bot`",file=file)

    @commands.command()
    async def credit(self,ctx):
        if await canUseCommand(ctx,2):
            await ctx.reply(await getDictStr(load_json(BotPaths.credits_file)))

    @commands.command()
    async def set_main(self, ctx,main:str):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            character=self.bot.characters
            if main in character.keys():
                self.bot.user_data[str(senderID)]["main"]=main
                await ctx.reply("You set your main to: "+main)
            else:
                await ctx.reply("That is not a valid character.")

    @commands.command()
    async def my_data(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            message=await getDictStr(self.bot.user_data[str(senderID)],True)
            await ctx.reply(message,delete_after=30)


    @commands.command()
    async def my_data_admin(self,ctx):
        senderID=ctx.author.id
        if await canUseCommand(ctx,1):
            await printLogToDc(self.bot,"debug",self.bot.user_data[str(senderID)])
            message=await getDictStr(self.bot.user_data[str(senderID)])
            await ctx.reply(message,delete_after=30)
            
    @commands.command()
    async def remove_me(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            self.bot.user_data.pop(str(senderID),None)
            if random.randint(0,1)==0:
                face=chooseFaceFromCategory(self.bot,"nervous")
            else:
                face=chooseFaceFromCategory(self.bot,"question")
            await ctx.reply("Who are you?\n"+face)

    @commands.command()
    async def save(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id == BOT_ROLE for role in ctx.author.roles):
                save_json(BotPaths.user_data_path,self.bot.user_data)
                await ctx.reply("Saving some stuff. "+chooseFaceFromCategory(self.bot,"concentrate"),delete_after=10)

    @commands.command()
    async def clear_loaded(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME:
                self.bot.user_data={}
        await ctx.reply("I forgor. Head empty...\n"+chooseFaceFromCategory(self.bot,"big_eyes"))

    @commands.command()
    async def clear_user_data(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME:
                self.bot.user_data={}
                save_json(BotPaths.user_data_path,{})
        await ctx.reply("I forgor. Head empty...\n"+chooseFaceFromCategory(self.bot,"big_eyes"))

    @commands.command()
    async def rand(self, ctx,sub:str=None, num:int=1):
        def getItemsType(items,type:str):
            returnItems=[]
            for curItem in items:
                if curItem.type==type:
                    returnItems.append(curItem)
            return returnItems
        def getItemsTier(items,tier:int):
            returnItems=[]
            for curItem in items:
                if curItem.tier==tier:
                    returnItems.append(curItem)
            return returnItems

        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if sub==None:
                botcommands=[
                    "`!rand char X`: Generates X random characters. (1 to 12)",
                    "`!rand char_pair X`: Generates X random character pairs. To play with a friend. (1 to 6)",
                    "`!rand item X`: Generates X random items. (1 to number of items)",
                    "`!rand item_gun X`: Generates X random gun items. (1 to number of gun items)",
                    "`!rand item_vit X`: Generates X random vitality items. (1 to number of vitality)",
                    "`!rand item_spi X`: Generates X random spirit items. (1 to number of spirit items)",
                    "`!rand item_tierI X`: Generate X random items from tier I. (1 to number of tier I items)",
                    "`!rand item_tierII X`: Generate X random items from tier II. (1 to number of tier II items)",
                    "`!rand item_tierIII X`: Generate X random items from tier III. (1 to number of tier III items)",
                    "`!rand item_tierIV X`: Generate X random items from tier IV. (1 to number of tier IV items)",
                ]
                await ctx.reply('\n'.join(botcommands))
            elif sub=="char":
                returnChars=""
                oChars=self.bot.characters.copy()
                if num<1:
                    num=1
                elif num>12:
                    num=12
                for i in range(num):
                    r=random.randint(0,len(oChars))
                    returnChars+=oChars[r]+"\n"
                    oChars.pop(r)
                await ctx.reply(returnChars)
            elif sub=="char_pair":
                returnChars=""
                oChars=self.bot.characters.copy()
                if num<1:
                    num=1
                elif num>6:
                    num=6
                for i in range(num):
                    smallList=""
                    r=random.randint(0,len(oChars))
                    smallList+=oChars[r]+"; "
                    oChars.pop(r)
                    r=random.randint(0,len(oChars))
                    smallList+=oChars[r]
                    oChars.pop(r)
                    returnChars+=smallList+"\n"
                await ctx.reply(returnChars)
            elif sub=="item":
                returnChars=""
                oItems=self.bot.items.copy()
                if num<1:
                    num=1
                elif num>len(oItems):
                    num=len(oItems)
                for i in range(num):
                    r=random.randint(0,len(oItems))
                    returnChars+=oItems[r].name.replace("_"," ")+"\n"
                    oItems.pop(r)
                await ctx.reply(returnChars)
            elif sub=="item_gun":
                returnChars=""
                oItems=getItemsType(self.bot.items,"gun")
                if num<1:
                    num=1
                elif num>len(oItems):
                    num=len(oItems)
                for i in range(num):
                    r=random.randint(0,len(oItems))
                    returnChars+=oItems[r].name.replace("_"," ")+"\n"
                    oItems.pop(r)
                await ctx.reply(returnChars)
            elif sub=="item_vit":
                returnChars=""
                oItems=getItemsType(self.bot.items,"vitality")
                if num<1:
                    num=1
                elif num>len(oItems):
                    num=len(oItems)
                for i in range(num):
                    r=random.randint(0,len(oItems))
                    returnChars+=oItems[r].name.replace("_"," ")+"\n"
                    oItems.pop(r)
                await ctx.reply(returnChars)
            elif sub=="item_spi":
                returnChars=""
                oItems=getItemsType(self.bot.items,"spirit")
                if num<1:
                    num=1
                elif num>len(oItems):
                    num=len(oItems)
                for i in range(num):
                    r=random.randint(0,len(oItems))
                    returnChars+=oItems[r].name.replace("_"," ")+"\n"
                    oItems.pop(r)
                await ctx.reply(returnChars)
            elif "item_tierI" in sub:
                returnChars=""
                if sub=="item_tierIV":
                    oItems=getItemsTier(self.bot.items,4)
                else:
                    oItems=getItemsTier(self.bot.items,sub.count("I"))
                if num<1:
                    num=1
                elif num>len(oItems):
                    num=len(oItems)
                for i in range(num):
                    r=random.randint(0,len(oItems))
                    returnChars+=oItems[r].name.replace("_"," ")+"\n"
                    oItems.pop(r)
                await ctx.reply(returnChars)
            else:
                await ctx.reply("I can't give you a random thing in that category."+chooseFaceFromCategory(self.bot,"nervous"))

    @commands.command()
    async def set_rank(self, ctx,rank:str=None):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if rank==None:
                await ctx.reply("Please provide a rank.")
            else:
                rank=rank.lower()
                if rank in self.bot.ranks.keys():
                    self.bot.user_data[str(senderID)]["rank"]=rank
                    await ctx.reply("Your rank has been set to: "+rank)
                else:
                    await ctx.reply("The rank you want to set does not exist.")

    @commands.command()
    async def people_at_rank(self, ctx,rank:str=None,r:int=0,online:int=0):
        r=abs(r)
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if rank==None:
                rank=self.bot.user_data[str(senderID)]["rank"]
                if rank=="None":
                    await ctx.reply("I can't use your rank as a base, because you haven't set your rank yet.")
                    return
            base=list(self.bot.ranks.keys()).index(rank)
            lookedForRanks=list(self.bot.ranks.keys())[max(0,base-r):min(base+r,len(list(self.bot.ranks.keys()))-1)]
            lookedForPeople=[]
            for i,(key,value) in enumerate(self.bot.user_data.items()):
                if key==str(senderID):
                    continue
                if value["rank"] in lookedForRanks:
                    if online:
                        for guild in self.bot.guilds:
                            member = guild.get_member(int(key))
                            if member:
                                if member.status!=discord.Status.online:
                                    continue
                    lookedForPeople.append((await self.bot.fetch_user(int(key))).display_name+": "+value["rank"])
            if len(lookedForPeople)!=0:
                await ctx.reply("These people have rank simmilar to what you are looking for:\n"+'\n'.join(lookedForPeople))
            else:
                if online:
                    await ctx.reply("No online people are in that rank. "+chooseFaceFromCategory(self.bot,"sad"))
                else:
                    await ctx.reply("No people found. "+chooseFaceFromCategory(self.bot,"sad"))










async def setup(bot):
    await bot.add_cog(Unorganized(bot))


