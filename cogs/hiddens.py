
import discord
from discord.ext import commands, tasks
import asyncio
import time
import random
import shutil

from own_utils import chooseFaceFromCategory, canUseCommand, format_duration, cleanChannel
from constants import CHANNEL_IDS
from user_bot_interaction import interact, getInteractValue, getGlobalInteractValue
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from constants import USER_CLEVER, FUNLOCK_SERVER_ID, BASE
from classes.bot_faces import Faces
from debug import setupFolders

#"hidden" commands (they are not listed in bot_help; KEEP IT THIS WAY)
#"a secret for everyone"
#haha ... reference

class Hiddens(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    """
    async def play_sound(self,ctx,path:str):
        if await canUseCommand(ctx,2):
            finished = asyncio.Event()
            start_time = time.monotonic()
            def after_playing(error):
                if error:
                    printLog("error",f"Playback error: {error}")
                elapsed = time.monotonic() - start_time

                printLog("error" if error else "debug",f"Audio callback after {elapsed:.2f}s; error={error!r}")
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

            source=discord.FFmpegPCMAudio(path)
            vc.play(source, after=after_playing)

            printLog("debug", f"Started playback: {path}")

            try:
                await finished.wait()
            finally:
                if not was_in and vc.is_connected():
                    await vc.disconnect()
    """
    
    async def play_sound(self, ctx, path: str,vcID:int=None):
        if vcID==None:
            if not await canUseCommand(ctx, 2):
                return
            if ctx.author.voice is None or ctx.author.voice.channel is None:
                await ctx.send("You must be in a voice channel.")
                return

            channel=ctx.author.voice.channel
            vc=ctx.voice_client
            was_connected=vc is not None

            if vc is None:
                vc=await channel.connect()
            elif vc.channel!=channel:
                await vc.move_to(channel)

            # Stop any previous playback before creating the new source.
            if vc.is_playing() or vc.is_paused():
                vc.stop()

            loop=asyncio.get_running_loop()
            finished=asyncio.Event()
            start_time=time.monotonic()

            def after_playing(error):
                elapsed=time.monotonic()-start_time
                if error:
                    printLog("error",f"Playback error after {elapsed:.2f}s: {error!r}")
                else:
                    printLog("debug",f"Playback finished after {elapsed:.2f}s")
                loop.call_soon_threadsafe(finished.set)

            source=None

            try:
                source=discord.FFmpegPCMAudio(path,before_options="-nostdin",options="-loglevel warning",)
                vc.play(source, after=after_playing)
                printLog("debug", f"Started playback: {path}")
                await finished.wait()
            except Exception as e:
                printLog("error",f"Could not play {path}: {e!r}")
                raise

            finally:
                if source is not None:
                    source.cleanup()

                if not was_connected and vc.is_connected():
                    await vc.disconnect()
        else:
            printLog("debug","A")
            beforeChannel=None
            channel=self.bot.get_channel(vcID)
            vc=ctx.voice_client
            was_connected=vc is not None

            if vc is None:
                vc=await channel.connect()
            elif vc.channel!=channel:
                beforeChannel=vc.channel
                await vc.move_to(channel)

            # Stop any previous playback before creating the new source.
            if vc.is_playing() or vc.is_paused():
                vc.stop()

            loop=asyncio.get_running_loop()
            finished=asyncio.Event()
            start_time=time.monotonic()

            def after_playing(error):
                elapsed=time.monotonic()-start_time
                if error:
                    printLog("error",f"Playback error after {elapsed:.2f}s: {error!r}")
                else:
                    printLog("debug",f"Playback finished after {elapsed:.2f}s")
                loop.call_soon_threadsafe(finished.set)

            source=None

            try:
                source=discord.FFmpegPCMAudio(path,before_options="-nostdin",options="-loglevel warning",)
                vc.play(source, after=after_playing)
                printLog("debug", f"Started playback: {path}")
                await finished.wait()
            except Exception as e:
                printLog("error",f"Could not play {path}: {e!r}")
                raise

            finally:
                if source is not None:
                    source.cleanup()

                if not was_connected and vc.is_connected():
                    await vc.disconnect()
                
                if beforeChannel!=None:
                    vc.move_to(beforeChannel)

    @commands.command()
    async def clean(self,ctx,many:int=None):
        if await canUseCommand(ctx,0):
            #cleanup
            if many==None:
                await ctx.reply("Range not specified.")
            else:
                if many==-1:
                    many=None
                await cleanChannel(self.bot,CHANNEL_IDS.BOTS_CHANNEL_ID,many)
    
    @commands.command()
    async def cleanDebug(self,ctx):
        if await canUseCommand(ctx,0):
            await ctx.reply("Cleaning up...")
            #delete debug folder
            folder_path=BASE / "debug"
            if folder_path.is_dir():
                shutil.rmtree(folder_path)
            await ctx.reply("Clean up finnished!")
            setupFolders()


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
    async def testaudio(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.TEST))

    @commands.command()
    async def silly(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.SILLY))

    @commands.command()
    async def sillyer(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.SILLYER))

    @commands.command()
    async def fish(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.FIH))

    @commands.command()
    async def FISH(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.FISH))

    @commands.command()
    async def portal(self,ctx):
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.PORTAL))

    @commands.command()
    async def dc_ping(self,ctx):
        await ctx.message.delete()
        for i in range(random.randint(1,5)):
            await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.PING))
            await asyncio.sleep(round(random.uniform(0.1,1),2))

    @commands.command()
    async def dc_ping_long(self,ctx):
        await ctx.message.delete()
        for i in range(random.randint(3,5)):
            await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.PING))
            await asyncio.sleep(round(random.uniform(10,2*60),2))

    @commands.command()
    async def play_any(self,ctx,path:str,vcID=None):
        if await canUseCommand(ctx,-1,False,False,False):
            if vcID=="T":
                vcID=CHANNEL_IDS.VC.TEST
            await self.play_sound(ctx,path,vcID)


    @commands.command()
    async def reset_the_timer(self,ctx, mention=None):
        guild=self.bot.get_guild(FUNLOCK_SERVER_ID)
        clever=guild.get_member(USER_CLEVER)
        extra=""
        if clever and clever.voice and clever.voice.channel:
            extra="\n<@534796790105505794> was here. "+chooseFaceFromCategory(Faces.FaceBigCategory.clever)
        if mention==None:
            extra+="\n\n-# mention a user in the command to add a point to the leaderboard "+chooseFaceFromCategory(Faces.nervous+" (not done yet)")
        await ctx.reply(f"The Degenerate Timer has been reset.\nTime before reset: {format_duration(time.time()-self.bot.degenTimer)}"+extra)
        self.bot.degenTimer=time.time()
    
    @commands.command()
    async def the_timer(self,ctx):
        await ctx.reply(f"The Degenerate Timer's time: {format_duration(time.time()-self.bot.degenTimer)}")

async def setup(bot):
    await bot.add_cog(Hiddens(bot))
