


import discord
from discord.ext import commands, tasks

from debug import printLog, printLogToDc, writeLog
from constants import CHANNEL_IDS
from own_utils import chooseFaceFromCategory, cleanChannel
from data_manage import load_txt
from constants import ME
from constants import WARNING_MESSAGE_IN_NAMETAG_CHANNEL_ID, WARNING_MESSAGE_IN_NAMETAG_CHANNEL
from constants import FLOOR_PLAN_MESSAGE, FLOOR_PLAN_MESSAGE_ID, RULES_MESSAGE, RULES_MESSAGE_ID
from constants import CHANNEL_IDS, ROLES, FUNLOCK_SERVER_ID, BOT_SERVER_SPEC_NAME
from constants import WHO_AM_I_ROLES, COLOR_CHOOSER_MESSAGE_ID, IAM_MESSAGE_ID, IAM_MESSAGE_CONTENT, COLOR_CHOOSER_MESSAGE_CONTENT, COLORED_ROLES
from classes.file_paths import BotPaths


import asyncio
import random

#on ready event

class Ready(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.Cog.listener()
    #@bot.event
    async def on_ready(self):
        if self.bot.opSys: #skip these running on windows (this assumes we test on windows and run on linux (or other op sys))
            asyncio.create_task(cleanChannel(self.bot,CHANNEL_IDS.BOT_DEBUG_CHANNEL,None))
            #send ME the hostname and ip of the raspberry so errors can be fixed
            import socket
            import getpass
            hostname=socket.gethostname()
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip=s.getsockname()[0]
            s.close()
            piUser=getpass.getuser()
            user=await self.bot.fetch_user(ME)
            await user.send(f"hostname: ```{hostname}```\nIP: ```{ip}```\nPi user: ```{piUser}```")

            #setup the bot name and profile picture
            guild=self.bot.get_guild(FUNLOCK_SERVER_ID)
            name=BOT_SERVER_SPEC_NAME[FUNLOCK_SERVER_ID]
            if guild:
                await guild.me.edit(nick=name)

            pfp_files=list(BotPaths.pfp_folder.glob("*.jpg"))
            if pfp_files:
                pfp_path=random.choice(pfp_files)
                printLog("info",f"Chosen pfp: {pfp_path}")
                with pfp_path.open("rb") as f:
                    await self.bot.user.edit(avatar=f.read())
                printLog("info",f"Changed PFP to {pfp_path.name}")
                
                #change name(role) color accordingly
                botRole=guild.get_role(ROLES.BOT_ROLE_NOT_AUTO_CREATED)
                if botRole is not None:
                    find=pfp_path.name.lower()
                    rgb=next((self.bot.characters[i]["color"] for i in self.bot.characters if i.lower().removeprefix("the ").split(" ")[0] in find),None)
                    if rgb is None:
                        printLog("error",f"Couldn't find color to match profile picture {pfp_path.name}.")
                        await printLogToDc(self.bot,"error",f"Couldn't find color to match profile picture {pfp_path.name}.")
                        rgb=[200,0,200]
                    color=discord.Color.from_rgb(*rgb)
                    await botRole.edit(color=color)
                    printLog("info","Changed role color.")
            else:
                printLog("error",f"No .jpg files found in {BotPaths.pfp_folder}")


        printLog("info",f"Bot connected as {self.bot.user}")

        guild = self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).guild
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)

        if self.bot.opSys: #skip these running on windows (same as before)
            face=chooseFaceFromCategory("big_eyes")
            with open(BotPaths.hotboot_file,"r") as f:
                channel=self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID)
                if channel:
                    if int(f.readline().strip())==0:
                        await channel.send("I'm awake!\nGood morning!\n"+face)
                    else:
                        await channel.send("Back online! "+face)
                await channel.send("Running bot version: "+self.bot.version+"\n"+self.bot.versionSTR)


        #print debug about updates
        #something is broken here
        #nothing seems to be sent
        tempData=load_txt(BotPaths.update_check_file)
        if len(tempData)!=0:
            await printLogToDc(self.bot,"info",tempData[0])


        #edit bot created messages
        channel=self.bot.get_channel(CHANNEL_IDS.ROLE_CHANNEL_ID)
        message=await channel.fetch_message(COLOR_CHOOSER_MESSAGE_ID)
        await message.edit(content=COLOR_CHOOSER_MESSAGE_CONTENT)
        for i in COLORED_ROLES:
            await message.add_reaction(COLORED_ROLES[i]["emoji"])

        message=await channel.fetch_message(IAM_MESSAGE_ID)
        await message.edit(content=IAM_MESSAGE_CONTENT)
        for i in WHO_AM_I_ROLES:
            await message.add_reaction(WHO_AM_I_ROLES[i]["emoji"])

        message=await channel.fetch_message(WARNING_MESSAGE_IN_NAMETAG_CHANNEL_ID)
        await message.edit(content=WARNING_MESSAGE_IN_NAMETAG_CHANNEL.replace("@",self.bot.user.mention).replace(" #",self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).mention))

        channel=self.bot.get_channel(CHANNEL_IDS.FLOOR_PLAN_CHANNEL_ID)
        message=await channel.fetch_message(FLOOR_PLAN_MESSAGE_ID)
        cont=FLOOR_PLAN_MESSAGE.replace("#13#",self.bot.get_channel(CHANNEL_IDS.STAT_TRACKER_CHANNEL_ID).mention)
        cont=cont.replace("#12#",self.bot.get_channel(CHANNEL_IDS.BOTS_CHANNEL_ID).mention)
        cont=cont.replace("#11#",self.bot.get_channel(CHANNEL_IDS.SUGGESTIONS_CHANNEL_ID).mention)
        cont=cont.replace("#10#",self.bot.get_channel(CHANNEL_IDS.PROJECT_SHARE).mention)
        cont=cont.replace("#9#",self.bot.get_channel(CHANNEL_IDS.PROJECTOR_ID).mention)
        cont=cont.replace("#8#",self.bot.get_channel(CHANNEL_IDS.SEMINAR_ROOM_ID).mention)
        cont=cont.replace("#7#",self.bot.get_channel(CHANNEL_IDS.CURIOSITY_ID).mention)
        cont=cont.replace("#6#",self.bot.get_channel(CHANNEL_IDS.LOBBY_CODES_ID).mention)
        cont=cont.replace("#5#",self.bot.get_channel(CHANNEL_IDS.LOUNGE_CHANNEL_ID).mention)
        cont=cont.replace("#4#",self.bot.get_channel(CHANNEL_IDS.PA_ID).mention)
        cont=cont.replace("#3#",self.bot.get_channel(CHANNEL_IDS.ROLE_CHANNEL_ID).mention)
        cont=cont.replace("#2#",self.bot.get_channel(CHANNEL_IDS.FLOOR_PLAN_CHANNEL_ID).mention)
        cont=cont.replace("#1#",self.bot.get_channel(CHANNEL_IDS.RULES_CHANNEL_ID).mention)
        cont=cont.replace("#0#",self.bot.get_channel(CHANNEL_IDS.JUST_ZIPLINE_ID).mention)
        await message.edit(content=cont)
        
        channel=self.bot.get_channel(CHANNEL_IDS.RULES_CHANNEL_ID)
        message=await channel.fetch_message(RULES_MESSAGE_ID)
        await message.edit(content=RULES_MESSAGE)

        #need a message in a channel? use this:
        """channel=self.bot.get_channel(1524176375903420466)
        if channel is None:
            channel=await self.bot.fetch_channel(1524176375903420466)
        await channel.send("New message!")"""

        #thess were needed once
        """
        forum = self.bot.get_channel(1544085021156184214)

        if not isinstance(forum, discord.ForumChannel):
            raise ValueError("The specified channel is not a forum channel.")

        existing = {tag.name for tag in forum.available_tags}

        for name in ["Tank","Support","Spirit Carry","Gun Carry","Spirit focus","Gun focus","Vitality focus","Lane bully","Assasin","Controll"]:
            if name in existing:
                continue

            await forum.create_tag(name=name)
        """

        
        #start the tick task
        #ticks every 1s
        tick_cog=self.bot.get_cog("tick_cog")
        if tick_cog and not tick_cog.tick.is_running():
            tick_cog.tick.start()
        
        #if not tick.is_running():
            #tick.start()
        
        if not self.bot.opSys: #skip this on linux (we want this when testing)
            a=""
            for command in self.bot.commands:
                cogName=command.cog.qualified_name if command.cog else "No Cog"
                commandName=command.name
                s=f"- {cogName}: {commandName}"
                a+=s+"\n"
            writeLog("log",a,"all_commands",False,False,"w","discord_deadlock_self.bot.py","on_ready",True)
            #exit()
            
        #this is last in on_ready()
        printLog("info",f"Bot running version: {self.bot.version}\t(on_ready finnished)")
        
        

async def setup(bot):
    await bot.add_cog(Ready(bot))