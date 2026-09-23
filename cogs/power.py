
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory, activeTimerExists, canUseCommand
from data_manage import save_json, load_json, load_txt, deep_save_json, deep_save_txt
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID

from classes.file_paths import BotPaths
from classes.bot_faces import Faces

#"power setting" commands

class Power(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def shutdown(self,ctx):
        if await canUseCommand(ctx,0):
            if activeTimerExists(self.bot):
                ctx.reply("Sorry, I can't shutdown now, there is at least 1 active timer.")
            else:
                if ctx.guild.voice_client:
                    await ctx.guild.voice_client.disconnect()
                save_json(BotPaths.user_data_path,self.bot.user_data)
                deep_save_json(BotPaths.user_data_file,self.bot.user_data)
                deep_save_txt(BotPaths.degen_timer_file,str(self.bot.degenTimer))
                await ctx.reply("Shuting down.\nGood night!\nᴗ˳ᴗ",delete_after=10)
                with open(BotPaths.restart_file,"w") as f:
                    f.write("0")
                await self.bot.close()
        else:
            me=await self.bot.fetch_user(ME)
            await ctx.send("Sorry only `"+str(me)+"` can shut me down.\n(Because then he knows I'm not running.)",delete_after=10)

    #aliases=["reload"] THIS DOESNT WORK
    #DO NOT PUT IT BACK
    @commands.command()
    async def restart(self,ctx,save:str="save"):
        await self.restartFunc(ctx,save,0)
    @commands.command()
    async def reload(self,ctx,save:str="save"):
        await self.restartFunc(ctx,save,0)

    @commands.command()
    async def update(self,ctx,versionNumWasUpdated:str=None):
        if versionNumWasUpdated==None:
            await ctx.reply("Aren't you forgetting something?\n\n-# Did you update the version number?\n-# Use `!update yes` if you did."+chooseFaceFromCategory(Faces.wink))
        else:
            await self.restartFunc(ctx,"save",1)

    async def restartFunc(self,ctx,save:str="save",tryUpdate:int=0):
        with open(BotPaths.lookForUpdates,"w") as f:
            f.write(str(tryUpdate))
        if await canUseCommand(ctx,2):
            if activeTimerExists(self.bot):
                ctx.reply("Sorry, I can't restart now, there is at least 1 active timer.")
            else:
                if ctx.guild.voice_client:
                    await ctx.guild.voice_client.disconnect()
                if save=="save":
                    save_json(BotPaths.user_data_path,self.bot.user_data)
                    deep_save_json(BotPaths.user_data_file,self.bot.user_data)
                    deep_save_txt(BotPaths.degen_timer_file,str(self.bot.degenTimer))
                with open(BotPaths.restart_file,"w") as f:
                    f.write("1")
                await ctx.reply("Shuting down.\nBe right back!\n"+chooseFaceFromCategory("blush_happy")+("\n-# Warning! I will not look for updates from any source! (use `!update`)" if tryUpdate!=1 else ""),delete_after=20)
                await self.bot.close()
    
    @commands.command()
    async def sleep(self,ctx,save:str="save"):
        if await canUseCommand(ctx,2):
            if activeTimerExists(self.bot):
                await ctx.reply("Sorry, I can't go to sleep now, there is at least 1 active timer.")
            else:
                if ctx.guild.voice_client:
                    await ctx.guild.voice_client.disconnect()
                if save=="save":
                    save_json(BotPaths.user_data_path,self.bot.user_data)
                    deep_save_txt(BotPaths.degen_timer_file,str(self.bot.degenTimer))
                    #deep_save_json(BotPaths.user_data_file,self.bot.user_data)
                
                with open(BotPaths.restart_file,"w") as f:
                    f.write("2")
                with open(BotPaths.pause_file,"r") as f:
                    pauseStart=f.readline().strip()
                    pauseEnd=f.readline().strip()
                
                await ctx.reply("Going to sleep\nI will be unavailable between "+pauseStart+" and "+pauseEnd+" CEST\n"+chooseFaceFromCategory("sleep"),delete_after=20)
                await self.bot.close()

async def setup(bot):
    await bot.add_cog(Power(bot))


