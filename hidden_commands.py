
import discord
from discord.ext import commands, tasks
import asyncio

from own_utils import chooseFaceFromCategory

#"hidden" commands (they are not listed in bot_help; KEEP IT THIS WAY)
#"a secret for everyone"
#haha ... reference

BOTS_CHANNEL_ID=0

class Hiddens(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    #silly, sillyer, fish and FISH should be made more professional (lot of copy paste)

    async def play_sound(self,ctx,path:str):
        senderID=ctx.author.id
        if ctx.channel.id==BOTS_CHANNEL_ID:
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
    async def pat(self,ctx):
        if ctx.channel.id==BOTS_CHANNEL_ID:
            await ctx.reply(chooseFaceFromCategory("pat"))

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


async def setup(bot):
    await bot.add_cog(Hiddens(bot))