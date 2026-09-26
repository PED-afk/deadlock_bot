


import discord
from discord.ext import commands, tasks

from debug import printLog, printLogToDc
from constants import COLORED_ROLES, WHO_AM_I_ROLES, COLOR_CHOOSER_MESSAGE_ID, IAM_MESSAGE_ID

#if reaction is added or removed from message
#moved here so main file is cleaner

class ReactionAddRemove(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id==COLOR_CHOOSER_MESSAGE_ID:
            lookingAt="color"
        elif payload.message_id==IAM_MESSAGE_ID:
            lookingAt="iam"
        else:
            printLog("event","User reacted to other message")
            return

        # Ignore the bot reacting to the message
        if payload.user_id==self.bot.user.id:
            printLog("event","Reaction added by bot")
            return
        
        role_id=None
        if lookingAt=="color":
            for role in COLORED_ROLES.values():
                if payload.emoji.name==role["emoji"]:
                    role_id=role["id"]
                    break
        elif lookingAt=="iam":
            for role in WHO_AM_I_ROLES.values():
                if payload.emoji.name==role["emoji"]:
                    role_id=role["id"]
                    break
        if role_id is None:
            printLog("event","Can't find role ID.")
            return
        guild=self.bot.get_guild(payload.guild_id)
        if guild is None:
            printLog("event","Can't find guild.")
            return
        member=guild.get_member(payload.user_id)
        role=guild.get_role(role_id)
        if member is None or role is None:
            printLog("event","Can't find member or role")
            return
        await member.add_roles(role)
        printLog("event","Role added successfuly")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        if payload.message_id==COLOR_CHOOSER_MESSAGE_ID:
            lookingAt="color"
        elif payload.message_id==IAM_MESSAGE_ID:
            lookingAt="iam"
        else:
            return

        # Ignore the bot reacting to the message
        if payload.user_id==self.bot.user.id:
            return

        role_id=None
        if lookingAt=="color":
            for role in COLORED_ROLES.values():
                if payload.emoji.name==role["emoji"]:
                    role_id=role["id"]
                    break
        elif lookingAt=="iam":
            for role in WHO_AM_I_ROLES.values():
                if payload.emoji.name==role["emoji"]:
                    role_id=role["id"]
                    break
        if role_id is None:
            return
        guild=self.bot.get_guild(payload.guild_id)
        if guild is None:
            return
        member=guild.get_member(payload.user_id)
        role=guild.get_role(role_id)
        if member is None or role is None:
            return
        await member.remove_roles(role)


async def setup(bot):
    await bot.add_cog(ReactionAddRemove(bot))
