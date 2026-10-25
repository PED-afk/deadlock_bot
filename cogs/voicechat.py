
import discord
from discord.ext import commands, tasks
import asyncio
import time
import random
import shutil

import yt_dlp

from own_utils import chooseFaceFromCategory, canUseCommand, format_duration, cleanChannel
from constants import CHANNEL_IDS
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from classes.bot_faces import Faces
from debug import setupFolders

#"hidden" commands (they are not listed in bot_help; KEEP IT THIS WAY)
#"a secret for everyone"
#haha ... reference

class VoiceChat(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.volume=1.0


    async def play_sound(self, ctx, path: str,volume:float=1.0):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("You must be in a voice channel.")
            return
        channel=ctx.author.voice.channel
        beforeChannel=None
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
            source=discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path,before_options="-nostdin",options="-loglevel warning",),volume=max(0.0, min(2.0, volume)))
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
    async def volume(self,ctx,volume:int=100):
        if await canUseCommand(ctx,2,True,True,True):
            if not (0<=volume and volume<=100):
                await ctx.send("Volume must be between 0 and 100.")
                return

            self.volume=volume/100
            voice=ctx.voice_client
            if voice and voice.is_playing():
                if isinstance(voice.source, discord.PCMVolumeTransformer):
                    voice.source.volume=self.volume
            await ctx.send(f"Volume set to **{volume}%**")
        
    @commands.command()
    async def stops(self,ctx):
        if await canUseCommand(ctx,2,True,True,True):
            await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.SILENCE),volume=1.0)


    @commands.command()
    async def play(self, ctx, *, url: str):
        def get_audio_info(url):
            with yt_dlp.YoutubeDL({"format": "bestaudio/best","noplaylist": True,"quiet": True,}) as ydl:
                return ydl.extract_info(url, download=False)
        if await canUseCommand(ctx,2,True,True,True):
            channel = ctx.author.voice.channel
            voice = ctx.voice_client

            if voice is None:
                voice = await channel.connect()
            elif voice.channel!=channel:
                await voice.move_to(channel)

            if voice.is_playing() or voice.is_paused():
                voice.stop()

            await ctx.send("Loading audio...")

            try:
                info = await asyncio.to_thread(get_audio_info, url)
                audio_url = info["url"]
                title = info.get("title", "Unknown title")

                FFMPEG_OPTIONS={
                    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    "options": "-vn",
                }
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS),
                    volume=self.volume
                )

                voice.play(source)
                await ctx.send(f"Now playing: **{title}**")

            except Exception as e:
                await ctx.send(f"Could not play audio: {e}")










async def setup(bot):
    await bot.add_cog(VoiceChat(bot))
