
import discord
from discord.ext import commands, tasks
import asyncio
import time
import random
import shutil

import yt_dlp

from own_utils import chooseFaceFromCategory, canUseCommand
from constants import MAX_MESSAGE_LEN, MAX_PLAYLIST_PER_USER, MAX_PLAYLIST_PER_USER_HARD
from debug import printLogToDc, printLog
from classes.file_paths import BotPaths
from classes.bot_faces import Faces

#commands to controll playing music/audio in voicechat

class PlayList():
    printLog("Info","Playlist reset.")
    PL_name=None
    queue=None
    userID=None
    curIDX=0
    supressLastAfterPlay=False


class VoiceChat(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.volume=1.0
        self.curentPlayList=PlayList()


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
                await vc.move_to(beforeChannel)


    
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
            self.curentPlayList.supressLastAfterPlay=True
            await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.SILENCE),volume=1.0)


    @commands.command()
    async def play(self, ctx, *, url: str):
        def get_audio_info(url):
            with yt_dlp.YoutubeDL({"format": "bestaudio/best","noplaylist": True,"quiet": True,}) as ydl:
                return ydl.extract_info(url, download=False)
        if not await canUseCommand(ctx,2,True,inVoice=True,tellReason=True):
            return
        def after_playing(error):
            if error:
                printLog("error",f"Playback error: {error}")
            
            if self.curentPlayList.supressLastAfterPlay or self.bot.dangerousPlayAfterOverride:
                self.curentPlayList.supressLastAfterPlay=False
                self.bot.dangerousPlayAfter=False
                return
            if self.curentPlayList.queue==None:
                self.bot.dangerousPlayAfter=False
                return
            self.curentPlayList.curIDX+=1
            if self.curentPlayList.curIDX==len(self.curentPlayList.queue):
                printLog("info","after_playing reset")
                self.curentPlayList=PlayList()
                return
            future=asyncio.run_coroutine_threadsafe(
                self.play(ctx,self.curentPlayList.queue[self.curentPlayList.curIDX]),
                self.bot.loop,
            )
        self.bot.dangerousPlayAfter=False
        
        channel=ctx.author.voice.channel
        voice=ctx.voice_client

        if voice is None:
            voice=await channel.connect()
        elif voice.channel!=channel:
            await voice.move_to(channel)

        if voice.is_playing() or voice.is_paused():
            voice.stop()

        await ctx.send("Loading audio...")

        try:
            info=await asyncio.to_thread(get_audio_info, url)
            audio_url=info["url"]
            title=info.get("title", "Unknown title")

            FFMPEG_OPTIONS={
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn",
            }
            source=discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS),
                volume=self.volume
            )

            voice.play(source,after=after_playing)
            await ctx.send(f"Now playing: **{title}**")

        except Exception as e:
            await ctx.send(f"Could not play audio: {e}")



    @commands.command()
    async def playlists(self, ctx):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        msg="You have the following playlist(s):\n==============================="
        extra="\n===============================\nPlay one with `!playPL <playlist name>`!\nSee what is in one of them with `!playlist <playlist name>`!"
        for i in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            curMsgLen=len(msg)+len(f"\n{i}")+len(extra)
            if curMsgLen>=MAX_MESSAGE_LEN:
                printLog("info",f"message longer than limit:{curMsgLen}/{MAX_MESSAGE_LEN}")
                break
            msg+=f"\n{i}"
        msg+=extra
        await ctx.reply(msg)
        
    @commands.command()
    async def playlist(self,ctx,name:str=None):
        def get_audio_info(url):
            with yt_dlp.YoutubeDL({"format": "bestaudio/best","noplaylist": True,"quiet": True,}) as ydl:
                return ydl.extract_info(url, download=False)
        if not await canUseCommand(ctx,2):
            return
        if name is None:
            await ctx.reply("Give me the name of the playlist you want to view.\nSee your playlists with `!playlists`!")
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nSee your playlists with `!playlists`!")
            return
        if len(self.bot.user_data[str(ctx.author.id)]["playlists"][name])==0:
            await ctx.reply("This playlist doesn't have any videos.\nAdd videos with `!addtoPL <playlist name> <youtube url>")
            return
        msg="This playlist has the following videos:"
        for url in self.bot.user_data[str(ctx.author.id)]["playlists"][name]:
            info=await asyncio.to_thread(get_audio_info, url)
            title=info.get("title", "Unknown title")
            curMsgLen=len(msg)+len(f"\n{title}")
            if curMsgLen>=MAX_MESSAGE_LEN:
                printLog("info",f"message longer than limit:{curMsgLen}/{MAX_MESSAGE_LEN}")
                break
            msg+=f"\n{title}"
        await ctx.reply(msg)
        
    @commands.command()
    async def createPL(self,ctx,name:str):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            self.bot.user_data[str(ctx.author.id)]["playlists"]={}
        if name in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You have a playlist with that name.\nSee your playlists with `!playlists`!")
            return
        if len(self.bot.user_data[str(ctx.author.id)]["playlists"])>=MAX_PLAYLIST_PER_USER and not await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply(f"You already have {MAX_PLAYLIST_PER_USER} playlists (which is the maximum).")
            return
        if len(self.bot.user_data[str(ctx.author.id)]["playlists"])>=MAX_PLAYLIST_PER_USER_HARD and await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply(f"You already have {MAX_PLAYLIST_PER_USER} playlists (which is the maximum).")
            return
        
        self.bot.user_data[str(ctx.author.id)]["playlists"][name]=[]
        await ctx.reply(f"Created playlist named {name}. Add links to it with `!addtoPL <youtube link/URL>`!")

    @commands.command()
    async def deletePL(self,ctx,name:str):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nSee your playlists with `!playlists`!")
            return
        
        self.bot.user_data[str(ctx.author.id)]["playlists"].pop(name, None)
        await ctx.reply(f"Deleted playlist named {name}.")
        
    @commands.command()
    async def playPL(self,ctx,name:str=None):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name is None:
            await ctx.reply("Give me the name of the playlist you want to play.\nYou can view your playlists with `!playlists`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nCreate one with `!createPL <playlist name>`!\nSee your playlists with `!playlists`!")
            return
        if self.curentPlayList.queue!=None and not await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply("There is a playlist already playing somewhere.\nUse `!stopPL` to stop it if it's yours!")
            return
        if len(self.bot.user_data[str(ctx.author.id)]["playlists"][name])==0:
            await ctx.reply("This playlist is empty.\nUse `!addtoPL <youtube link/URL>` to add more links to it!")
            return
        self.curentPlayList.curIDX=0
        self.curentPlayList.userID=ctx.author.id
        self.curentPlayList.queue=list(self.bot.user_data[str(ctx.author.id)]["playlists"][name])
        self.curentPlayList.PL_name=name
        await ctx.reply(f"Playing playlist {name}")
        await ctx.invoke(self.bot.get_command("play"),url=self.bot.user_data[str(ctx.author.id)]["playlists"][name][0])
        
    @commands.command()
    async def stopPL(self,ctx):
        if not await canUseCommand(ctx,2):
            return
        if self.curentPlayList.userID==None:
            await ctx.reply("There isn't a active playlist.")
            return
        if self.curentPlayList.userID!=ctx.author.id and not await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply("You are not the user who started this playlist.\nThe playlist must end or the user must stop it.")
            return
        
        printLog("info","stopPL reset")
        self.curentPlayList=PlayList()
        self.curentPlayList.supressLastAfterPlay=True
        await ctx.reply("Stoping playlist.")
        await self.play_sound(ctx,str(BotPaths.sounds_folder / BotPaths.vcSounds.SILENCE),volume=1.0)

    @commands.command()
    async def playNEXT(self,ctx):
        if not await canUseCommand(ctx,2):
            return
        if self.curentPlayList.userID!=ctx.author.id and not await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply("You are not the user who started this playlist.\nThe playlist must end or the user must stop it.")
            return
        if self.curentPlayList.userID==None:
            await ctx.reply("There isn't a active playlist.")
            return
        self.curentPlayList.curIDX+=1
        if self.curentPlayList.curIDX>=len(self.curentPlayList.queue):
            await ctx.reply("You reached the end of the playlist.")
            printLog("info","playNEXT reset")
            self.curentPlayList=PlayList()
            return
        await ctx.reply("Playing next video.")
        self.curentPlayList.supressLastAfterPlay=True
        await ctx.invoke(self.bot.get_command("play"),url=self.bot.user_data[str(ctx.author.id)]["playlists"][self.curentPlayList.PL_name][self.curentPlayList.curIDX])
        
    @commands.command()
    async def playPREV(self,ctx):
        if not await canUseCommand(ctx,2):
            return
        if self.curentPlayList.userID!=ctx.author.id and not await canUseCommand(ctx,1,tellReason=False):
            await ctx.reply("You are not the user who started this playlist.\nThe playlist must end or the user must stop it.")
            return
        if self.curentPlayList.userID==None:
            await ctx.reply("There isn't a active playlist.")
            return
        self.curentPlayList.curIDX-=1
        if self.curentPlayList.curIDX<0:
            self.curentPlayList.curIDX=0
            await ctx.reply("You are at the beginning of the playlist.")
            return
        await ctx.reply("Playing previous video.")
        self.curentPlayList.supressLastAfterPlay=True
        await ctx.invoke(self.bot.get_command("play"),url=self.bot.user_data[str(ctx.author.id)]["playlists"][self.curentPlayList.PL_name][self.curentPlayList.curIDX])

    @commands.command()
    async def addtoPL(self,ctx,name:str,url:str):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nCreate one with `!createPL <playlist name>`!\nSee your playlists with `!playlists`!")
            return
        self.bot.user_data[str(ctx.author.id)]["playlists"][name].append(url)
        await ctx.reply("Added url to playlist.")

    @commands.command()
    async def removeFromPL(self,ctx,name:str,url:str):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nCreate one with `!createPL <playlist name>`!\nSee your playlists with `!playlists`!")
            return
        if not url.startswith("title:"):
            if url not in self.bot.user_data[str(ctx.author.id)]["playlists"][name]:
                await ctx.reply("You don't have this url in your playlist.")
                return
            self.bot.user_data[str(ctx.author.id)]["playlists"][name].remove(url)
            await ctx.reply(f"Removed video from playlist.")
        else:
            def get_audio_info(url):
                with yt_dlp.YoutubeDL({"format": "bestaudio/best","noplaylist": True,"quiet": True,}) as ydl:
                    return ydl.extract_info(url, download=False)
            delTitle=url.removeprefix("title:")
            for link in self.bot.user_data[str(ctx.author.id)]["playlists"][name]:
                info=await asyncio.to_thread(get_audio_info, link)
                title=info.get("title", "Unknown title")
                if title==delTitle:
                    self.bot.user_data[str(ctx.author.id)]["playlists"][name].remove(link)
                    await ctx.reply(f"Removed {title} from playlist.")
                    break
                    
        
    @commands.command()
    async def removeFromPL_id(self,ctx,name:str,sId:int):
        if not await canUseCommand(ctx,2):
            return
        if "playlists" not in self.bot.user_data[str(ctx.author.id)]:
            await ctx.reply("You don't have any playlists.\nCreate one with `!createPL <playlist name>`!")
            return
        if name not in self.bot.user_data[str(ctx.author.id)]["playlists"]:
            await ctx.reply("You don't have a playlist with that name.\nCreate one with `!createPL <playlist name>`!\nSee your playlists with `!playlists`!")
            return
        if sId>len(self.bot.user_data[str(ctx.author.id)]["playlists"][name]):
            await ctx.reply("You don't have this many songs in your playlist")
            return
        self.bot.user_data[str(ctx.author.id)]["playlists"][name].pop(sId-1)
        await ctx.reply(f"Removed video from playlist.")




async def setup(bot):
    await bot.add_cog(VoiceChat(bot))
