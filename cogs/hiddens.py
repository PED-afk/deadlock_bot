
import discord
from discord.ext import commands, tasks
import asyncio
import time

from own_utils import chooseFaceFromCategory, canUseCommand, format_duration, printLog
from constants import ME, BOT_ROLE, BOTS_CHANNEL_ID
from user_bot_interaction import interact, getInteractValue, getGlobalInteractValue
from debug import printLogToDc

#"hidden" commands (they are not listed in bot_help; KEEP IT THIS WAY)
#"a secret for everyone"
#haha ... reference

class Hiddens(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    async def play_sound(self,ctx,path:str):
        if await canUseCommand(ctx):
            def after_playing(error):
                if error:
                    print(f"Playback error: {error}")
                self.bot.loop.call_soon_threadsafe(finished.set)
                
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send("You must be in a voice channel.")
                return
            
            channel=ctx.author.voice.channel
            was_in=ctx.voice_client is not None

            if was_in:
                vc=ctx.voice_client
                if vc.channel != channel:
                    await vc.move_to(channel)
            else:
                vc=await channel.connect()

            if vc.is_playing():
                vc.stop()

            finished=asyncio.Event()
            #source = discord.PCMAudio(str(bot.sounds_folder / "voicechat" / "silly(128k).wav"))
            source=discord.PCMAudio(open(path,"rb"))
            vc.play(source, after=after_playing)

            try:
                await finished.wait()
            finally:
                if not was_in and vc.is_connected():
                    await vc.disconnect()




    @commands.command()
    async def clean(self,ctx,many:int=None):
        if canUseCommand(ctx,0):
            #cleanup
            if many==None:
                await ctx.reply("Range not specified.")
            else:
                if many==-1:
                    many=None
                async for msg in self.bot.get_channel(BOTS_CHANNEL_ID).history(limit=many):
                    try:
                        await msg.delete()
                    except discord.Forbidden:
                        printLog("error","I don't have permission to delete this messages.")
                        break
                    except discord.HTTPException:
                        pass


    async def petFunc(self,ctx):
        if await canUseCommand(ctx):
            interact(self.bot,2,"happy",int(ctx.author.id))
            curVal=max(getInteractValue(self.bot,"happy",int(ctx.author.id)),getGlobalInteractValue(self.bot,"happy"))
            if curVal<10:
                await ctx.reply(chooseFaceFromCategory("pat"))
            elif curVal<15:
                await ctx.reply(chooseFaceFromCategory("concerned")+"\nStawp")
            elif curVal<20:
                await ctx.reply(chooseFaceFromCategory("annoyed")+"\nStop.")
            else:
                await ctx.reply(chooseFaceFromCategory("neutral"))

    @commands.command()
    async def pat(self,ctx):
        await self.petFunc(ctx)
    @commands.command()
    async def pet(self,ctx):
        await self.petFunc(ctx)

    @commands.command()
    async def cogTest(self,ctx):
        if await canUseCommand(ctx):
            await ctx.reply("cog works")

    @commands.command()
    async def silly(self,ctx):
        await self.play_sound(ctx,str(self.bot.sounds_folder / "voicechat" / "silly(128k).pcm"))

    @commands.command()
    async def sillyer(self,ctx):
        await self.play_sound(ctx,str(self.bot.sounds_folder / "voicechat" / "sillyer(128k).pcm"))

    @commands.command()
    async def fish(self,ctx):
        await self.play_sound(ctx,str(self.bot.sounds_folder / "voicechat" / "FIH(128k).pcm"))

    @commands.command()
    async def FISH(self,ctx):
        await self.play_sound(ctx,str(self.bot.sounds_folder / "voicechat" / "FISH.pcm"))

    @commands.command()
    async def portal(self,ctx):
        await self.play_sound(ctx,str(self.bot.sounds_folder / "voicechat" / "portal.pcm"))

    @commands.command()
    async def reset_the_timer(self,ctx):
        await ctx.reply(f"The Degenerate Timer has been reset.\nTime before reset: {format_duration(time.time()-self.bot.degenTimer)}")
        self.bot.degenTimer=time.time()
    @commands.command()
    async def the_timer(self,ctx):
        await ctx.reply(f"The Degenerate Timer's time: {format_duration(time.time()-self.bot.degenTimer)}")

async def setup(bot):
    await bot.add_cog(Hiddens(bot))
