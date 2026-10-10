
import discord
from discord.app_commands.tree import CommandTree
from discord.ext import commands, tasks
from discord.ext.commands.bot import _default

import time

from classes.file_paths import BotPaths
from classes.item import DeadlockItem
from data_manage import load_json, save_json, deep_load_txt, deep_load_json, load_txt
from constants import GREET_CD, MESSAGE_CD


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
        await self.load_extension("cogs.member_join_cog")
        await self.load_extension("cogs.show_errors_cog")
        await self.load_extension("cogs.games_cog")
        #await self.load_extension("cogs.priority_cog")
    
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        
        def loadItemsProper(items:list[str])->list[DeadlockItem]:
            """
            Creates and returns a list of DeadlockItem objects from a list of str
            Str-s must have at least 3 arguments in them searated by ` `
            """
            newItems=[]
            for curItem in items:
                curItemParts=curItem.split(" ")
                newItems.append(DeadlockItem(curItemParts[0],int(curItemParts[1]),curItemParts[2]))
            return newItems
        
        
        
        self.autoMessages=load_json(BotPaths.autoMessage_file)
        self.autoMessagesOld=load_json(BotPaths.autoMessage_file_gitignored)

        self.autoMessagesOld.update(self.autoMessages)
        save_json(BotPaths.autoMessage_file_gitignored,self.autoMessagesOld)
        self.autoMessages=self.autoMessagesOld
        del self.autoMessagesOld
        for key, value in self.autoMessages.items():
            if key=="delAll":
                self.autoMessages={}
                save_json(BotPaths.autoMessage_file_gitignored,self.autoMessages)
                break


        self.startTimers={"A":11*60,"B":11*60}
        self.timers={"A":{"time":None,"paused":False},"B":{"time":None,"paused":False}}

        self.shhMod={}
        self.lastShhCheck=time.time()//1


        self.bootTime=time.time()//1
        self.version="0.12.11"
        self.versionSTR="The Shop is now available\nBuy items to participate in the next updates minigame(s)"



        self.messageCD=MESSAGE_CD
        self.greetCD=GREET_CD
        self.degenTimer=int(float(deep_load_txt(BotPaths.degen_timer_file)))

        self.user_data=deep_load_json(BotPaths.user_data_file)
        idSTR="global"
        if idSTR not in self.user_data.keys():
            self.user_data[idSTR]={}
            self.user_data[idSTR]["main"]="None"
            self.user_data[idSTR]["steamID"]="None"
            self.user_data[idSTR]["steamID3"]="None"
            self.user_data[idSTR]["steamID64"]="None"
            self.user_data[idSTR]["rank"]="None"
            self.user_data[idSTR]["lvl"]=1
            self.user_data[idSTR]["XP"]=0
            self.user_data[idSTR]["wins"]=0
        if "money" not in self.user_data[idSTR].keys():
            self.user_data[idSTR]["money"]={}
            self.user_data[idSTR]["money"]["unsecured"]=0
            self.user_data[idSTR]["money"]["secured"]=0
        if "items" not in self.user_data[idSTR].keys():
            self.user_data[idSTR]["items"]=[]
        if "hidden" not in self.user_data[idSTR].keys():
            self.user_data[idSTR]["hidden"]={}
            self.user_data[idSTR]["hidden"]["messageCD"]=0
            self.user_data[idSTR]["hidden"]["greetMessageCD"]=0
        if "interact" not in self.user_data[idSTR]["hidden"].keys():
            self.user_data[idSTR]["hidden"]["interact"]={}

        self.characters=load_json(BotPaths.characters_file_json)
        self.maxLevel=self.characters[list(self.characters.keys())[0]]["maxLvl"]

        self.items=loadItemsProper(load_txt(BotPaths.items_file))
        self.map_graph=load_json(BotPaths.map_graph_file)

        self.ranks=load_json(BotPaths.ranks_file)



        def opsysCheck():
            import platform
            try:
                platform.freedesktop_os_release()
            except:
                return False
            return True

        self.opSys=opsysCheck()