

import discord
from discord.ext import commands, tasks
import asyncio
import time
import random

from own_utils import chooseFaceFromCategory, canUseCommand
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID, WHO_AM_I_ROLES
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths

#tools for everyone

class Tools(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def onlines(self,ctx):
        if await canUseCommand(ctx,3,inChannel=False):
            role_id=WHO_AM_I_ROLES["ping_if_online"]["id"]

            role=ctx.guild.get_role(role_id)
            if role is None:
                printLog("error","`ping if online` role not found.")
                return
            online_members=[member.mention for member in role.members if member.status == discord.Status.online and member.id!=ctx.author.id]
            mentions="\n".join(online_members)

            if len(online_members)!=0:
                message=f"{ctx.author.mention} is looking for people to play with!\n\n{mentions}"
                await ctx.send(message)
            else:
                await ctx.send("No users online.")
        await ctx.message.delete()

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
                await ctx.reply("I can't give you a random thing in that category."+chooseFaceFromCategory("nervous"))


   
async def setup(bot):
    await bot.add_cog(Tools(bot))
