
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory, activeTimerExists
from data_manage import save_json, load_json, load_txt
from dc_ids import ME,BOT_ROLE,BOTS_CHANNEL_ID

#"power setting" commands

class Power(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def shutdown(self,ctx):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            me=await self.bot.fetch_user(ME)
            if senderID==ME:
                if activeTimerExists():
                    ctx.reply("Sorry, I can't shutdown now, there is at least 1 active timer.")
                else:
                    if ctx.guild.voice_client:
                        await ctx.guild.voice_client.disconnect()
                    save_json(self.bot.user_data_path,self.bot.user_data)
                    await ctx.reply("Shuting down.\nGood night!\nᴗ˳ᴗ",delete_after=10)
                    with open(self.bot.restart_file,"w") as f:
                        f.write("0")
                    await self.bot.close()
            elif any(role.id==BOT_ROLE for role in ctx.author.roles):
                await ctx.send("Sorry only `"+str(me)+"` can shut me down.\n(Because then he knows I'm not running.)",delete_after=10)
                
    @commands.command(aliases=["reload"])
    async def restart(self,ctx,save:str="save"):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id==BOT_ROLE for role in ctx.author.roles):
                if activeTimerExists():
                    ctx.reply("Sorry, I restart now, there is at least 1 active timer.")
                else:
                    if ctx.guild.voice_client:
                        await ctx.guild.voice_client.disconnect()
                    if save=="save":
                        save_json(self.bot.user_data_path,self.bot.user_data)
                    with open(self.bot.restart_file,"w") as f:
                        f.write("1")
                    await ctx.reply("Shuting down.\nBe right back!\n"+chooseFaceFromCategory(self.bot,"blush_happy"),delete_after=20)
                    await self.bot.close()
    
    @commands.command()
    async def sleep(self,ctx,save:str="save"):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
            if senderID==ME or any(role.id==BOT_ROLE for role in ctx.author.roles):
                if activeTimerExists():
                    await ctx.reply("Sorry, I can't go to sleep now, there is at least 1 active timer.")
                else:
                    if ctx.guild.voice_client:
                        await ctx.guild.voice_client.disconnect()
                    if save=="save":
                        save_json(self.bot.user_data_path,self.bot.user_data)
                    
                    with open(self.bot.restart_file,"w") as f:
                        f.write("2")
                    with open(self.bot.pause_file,"r") as f:
                        pauseStart=f.readline().strip()
                        pauseEnd=f.readline().strip()
                    
                    await ctx.reply("Going to sleep\nI will be unavailable between "+pauseStart+" and "+pauseEnd+" CEST\n"+chooseFaceFromCategory(self.bot,"sleep"),delete_after=20)
                    await self.bot.close()
async def setup(bot):
    await bot.add_cog(Power(bot))


