

import discord
from discord.ext import commands, tasks

import os
from dotenv import load_dotenv
import time
import random
import aiohttp

from data_manage import save_json, load_json, load_txt, deep_load_json, deep_load_txt
"""
load_txt returns a list of str from the filepath
load_json and save_json loads from and saves to json files

neither does anything else other than open the file on the filepath and load the data from it
"""
from own_utils import chooseFaceFromCategory, canUseCommand
from debug import printLog, printLogToDc
from constants import HERO_ID_MAP, RANK_NAMES, RANK_COLORS, BASE, ME, BOT_ROLE, BOTS_CHANNEL_ID, BOT_DEBUG_CHANNEL, MESSAGE_CD, VOICE_CHANNEL_CAT_NAME_PREFIX, BOT_SECRET_NICKNAMES, GREET_CD
from constants import ROLE_CHANNEL_ID, WHO_AM_I_ROLES, COLOR_CHOOSER_MESSAGE_ID, IAM_MESSAGE_ID, IAM_MESSAGE_CONTENT, COLOR_CHOOSER_MESSAGE_CONTENT, COLORED_ROLES

from classes.item import Item
from classes.file_paths import BotPaths
from user_bot_interaction import interact, getGlobalInteractValue, getInteractValue, wasGreeted, botGreets


#Set up the bot with a command prefix
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.voice_states = True

intents.reactions = True
intents.members = True
intents.guilds = True

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("cogs.hiddens")
        await self.load_extension("cogs.timer")
        await self.load_extension("cogs.power")
        await self.load_extension("cogs.unorganized")
        await self.load_extension("cogs.debugcog")
        #await self.load_extension("cogs.priority_cog")

#bot=commands.Bot(command_prefix='!', intents=intents)
#this does NOT work with cogs for some reason

bot=MyBot(command_prefix='!', intents=intents)


async def fetch_hero_id_to_name() -> dict[int, str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.deadlock-api.com/v1/heroes", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return HERO_ID_MAP
                data = await resp.json()
                result = {}
                for h in data:
                    hid = h.get("id") or h.get("hero_id")
                    hname = h.get("name") or h.get("hero_name") or h.get("display_name")
                    if hid and hname:
                        result[int(hid)] = hname
                return result if result else HERO_ID_MAP
    except Exception:
        return HERO_ID_MAP

async def fetch_most_played(steam_id_64: int, top_n: int = 3) -> list[dict] | None:
    account_id = steam_id_64 - 76561197960265728
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.deadlock-api.com/v1/players/{account_id}/hero-stats"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if not data:
                    return None
                hero_map = await fetch_hero_id_to_name()
                sorted_heroes = sorted(data, key=lambda x: x.get("matches_played", 0), reverse=True)
                result = []
                for h in sorted_heroes[:top_n]:
                    hero_id = h.get("hero_id")
                    name = hero_map.get(hero_id, f"Hero {hero_id}")
                    matches = h.get("matches_played", 0)
                    wins = h.get("wins", 0)
                    winrate = round(wins / matches * 100) if matches > 0 else 0
                    kda = round((h.get("kills", 0) + h.get("assists", 0)) / max(h.get("deaths", 1), 1), 2)
                    result.append({"name": name, "matches": matches, "wins": wins, "winrate": winrate, "kda": kda})
                return result
    except Exception:
        return None

async def assign_hero_role(member: discord.Member, hero_name: str):
    guild = member.guild
    all_heroes = list(bot.characters.keys())
    existing = [r for r in member.roles if r.name in all_heroes]
    if existing:
        await member.remove_roles(*existing, reason="Hero role update")
    role = discord.utils.get(guild.roles, name=hero_name)
    if role is None:
        role = await guild.create_role(name=hero_name, reason="Auto-created hero role")
    await member.add_roles(role, reason="Main hero assigned")

class MainPickerView(discord.ui.View):
    def __init__(self, author: discord.Member, heroes: list[dict]):
        super().__init__(timeout=60)
        self.author = author
        for h in heroes:
            btn = discord.ui.Button(label=h["name"], style=discord.ButtonStyle.primary)
            async def callback(interaction: discord.Interaction, hero=h):
                if interaction.user.id != self.author.id:
                    await interaction.response.send_message("These aren't your buttons!", ephemeral=True)
                    return
                senderID = str(interaction.user.id)
                bot.user_data[senderID]["main"] = hero["name"]
                await assign_hero_role(interaction.user, hero["name"])
                await interaction.response.edit_message(content=f"Main set to **{hero['name']}**! Role assigned.", view=None, embed=None)
            btn.callback = callback
            self.add_item(btn)

async def fetch_rank_from_api(steam_id_64: int) -> tuple[str, int] | None:
    account_id = steam_id_64 - 76561197960265728
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.deadlock-api.com/v1/players/{account_id}/mmr-history"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if not data:
                    return None
                recent = sorted(data, key=lambda x: x.get("start_time", 0))[-20:]
                # weight last 5 matches double, then take highest division from weighted mode
                weighted = [x.get("division") for x in recent if x.get("division") is not None]
                weighted += [x.get("division") for x in recent[-5:] if x.get("division") is not None]
                if not weighted:
                    return None
                division = max(set(weighted), key=weighted.count)
                # also bump up to peak division if it appears at least twice
                peak = max(weighted)
                if weighted.count(peak) >= 2:
                    division = peak
                matching = [x for x in recent if x.get("division") == division]
                division_tier = matching[-1].get("division_tier")
                if division_tier is None:
                    return None
                idx = division - 1
                if 0 <= idx < len(RANK_NAMES):
                    return (RANK_NAMES[idx], division_tier)
                return None
    except Exception:
        return None

async def assign_rank_role(member: discord.Member, rank: str):
    guild = member.guild
    rank_cap = rank.capitalize()
    existing = [r for r in member.roles if r.name.lower() in RANK_NAMES]
    if existing:
        await member.remove_roles(*existing, reason="Rank update")
    role = discord.utils.get(guild.roles, name=rank_cap)
    if role is None:
        role = await guild.create_role(
            name=rank_cap,
            color=RANK_COLORS.get(rank, discord.Color.default()),
            reason="Auto-created rank role from Deadlock API"
        )
    await member.add_roles(role, reason="Rank assigned from Deadlock API")

def loadItemsProper(items):
    newItems=[]
    for curItem in items:
        curItemParts=curItem.split(" ")
        newItems.append(Item(curItemParts[0],int(curItemParts[1]),curItemParts[2]))
    return newItems


@bot.event
async def on_ready():
    guild=bot.get_guild(123456789012345678)
    if guild:
        await guild.me.edit(nick=bot.name)

    pfp_files=list(BotPaths.pfp_folder.glob("*.jpg"))
    if pfp_files:
        pfp_path=random.choice(pfp_files)
        printLog("info",f"Chosen pfp: {pfp_path}")
        with pfp_path.open("rb") as f:
            await bot.user.edit(avatar=f.read())
        printLog("info",f"Changed PFP to {pfp_path.name}")
    else:
        printLog("error",f"No .jpg files found in {BotPaths.pfp_folder}")


    printLog("info",f"Bot connected as {bot.user}")

    guild = bot.get_channel(BOTS_CHANNEL_ID).guild
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)

    #cleanup
    async for msg in bot.get_channel(BOTS_CHANNEL_ID).history(limit=None):
        try:
            await msg.delete()
        except discord.Forbidden:
            print("I don't have permission to delete this messages.")
            break
        except discord.HTTPException:
            pass
    
    face=chooseFaceFromCategory("big_eyes")

    with open(BotPaths.hotboot_file,"r") as f:
        if int(f.readline().strip())==0:
            await bot.get_channel(BOTS_CHANNEL_ID).send("I'm awake!\nGood morning!\n"+face)
        else:
            await bot.get_channel(BOTS_CHANNEL_ID).send("Back online! "+face)

    tempData=load_txt(BotPaths.update_check_file)
    if len(tempData)!=0:
        await bot.get_channel(BOT_DEBUG_CHANNEL).send(tempData)


    #edit the role select messages
    channel=bot.get_channel(ROLE_CHANNEL_ID)
    message=await channel.fetch_message(COLOR_CHOOSER_MESSAGE_ID)
    await message.edit(content=COLOR_CHOOSER_MESSAGE_CONTENT)
    for i in COLORED_ROLES:
        await message.add_reaction(COLORED_ROLES[i]["emoji"])

    message=await channel.fetch_message(IAM_MESSAGE_ID)
    await message.edit(content=IAM_MESSAGE_CONTENT)
    for i in WHO_AM_I_ROLES:
        await message.add_reaction(WHO_AM_I_ROLES[i]["emoji"])

    if not tick.is_running():
        tick.start()

@bot.event
async def on_message(message):
    if message.author.bot or message.webhook_id is not None or message.author == bot.user:
        return
    idINT=message.author.id
    idSTR=str(idINT)
    if message.reference:
        repliedTo=await message.channel.fetch_message(message.reference.message_id)
        if repliedTo.author.id == bot.user.id:
            thankingMessages=["thank you!","thank you","thanks!","thanks"]
            if any(t in message.content.lower() for t in thankingMessages):
                if any(t in message.content.lower() for t in BOT_SECRET_NICKNAMES):
                    interact(bot,3,"thank",idINT)
                    intVal=max(getInteractValue(bot,"thank",idINT),getGlobalInteractValue(bot,"thank"))
                    if intVal<=10:
                        if "My brain" in repliedTo.content:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                        else:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("spark"))
                    else:
                        await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))
                else:
                    interact(bot,1,"thank",idINT)
                    intVal=max(getInteractValue(bot,"thank",idINT),getGlobalInteractValue(bot,"thank"))
                    if intVal<=10:
                        if "My brain" in repliedTo.content:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("brain_hurt"))
                        else:
                            await message.reply("You're welcome!\n"+chooseFaceFromCategory("pat"))
                    else:
                        await message.reply("You're welcome.\n"+chooseFaceFromCategory("neutral"))


    if str(message.author.id) not in bot.user_data.keys():
        bot.user_data[idSTR]={}
        bot.user_data[idSTR]["main"]="None"
        bot.user_data[idSTR]["steamID"]="None"
        bot.user_data[idSTR]["steamID3"]="None"
        bot.user_data[idSTR]["steamID64"]="None"
        bot.user_data[idSTR]["rank"]="None"
        bot.user_data[idSTR]["lvl"]=1
        bot.user_data[idSTR]["XP"]=0
        bot.user_data[idSTR]["wins"]=0
    if "money" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["money"]={}
        bot.user_data[idSTR]["money"]["unsecured"]=0
        bot.user_data[idSTR]["money"]["secured"]=0
    if "items" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["items"]=[]
    if "hidden" not in bot.user_data[idSTR].keys():
        bot.user_data[idSTR]["hidden"]={}
        bot.user_data[idSTR]["hidden"]["messageCD"]=0
        bot.user_data[idSTR]["hidden"]["greetMessageCD"]=0
    if "interact" not in bot.user_data[idSTR]["hidden"].keys():
        bot.user_data[idSTR]["hidden"]["interact"]={}


    
    if message.content[0]!="!" and time.time()>=bot.user_data[idSTR]["hidden"]["messageCD"]:
        bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+bot.messageCD
        bonusM=1

        users_in_voice = []

        for guild in bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    users_in_voice.append(str(member.id)+" in "+voice_channel.name)
        if len(users_in_voice)!=0:
            givesBonus={
                "good luck":{"bonus":0.5,"alias":{"name":" gl ","bonus":0.25}},
                "have fun":{"bonus":0.5,"alias":{"name":" hf ","bonus":0.25}},
            }
            for i,key in enumerate(givesBonus):
                if key in message.content:
                    bonusM+=givesBonus[key]["bonus"]
                elif givesBonus[key]["alias"]["name"] in message.content:
                    bonusM+=givesBonus[key]["alias"]["bonus"]

        lenght=len(message.content)//10
        bot.user_data[idSTR]["money"]["unsecured"]+=100+random.randint(0,lenght)*bonusM
        bot.user_data[idSTR]["XP"]+=1+random.randint(0,lenght)*bonusM
        level=bot.user_data[idSTR]["lvl"]
        if level<bot.maxLevel:
            if bot.user_data[idSTR]["XP"]>=100+2**(level/4)+level:
                bot.user_data[idSTR]["XP"]-=100+2**(level/4)+level
                bot.user_data[idSTR]["lvl"]+=1

    greetAmount=await wasGreeted(message,bot.user.id)
    if greetAmount!=0 and time.time()>=bot.user_data[idSTR]["hidden"]["greetMessageCD"]:
        bot.user_data[idSTR]["hidden"]["messageCD"]=time.time()+bot.greetCD
        await message.reply(botGreets(greetAmount,message.author.mention))
        return


    if message.content.lower() in ["reset the timer","reset timer","!reset_the_timer","0 days without degenerate nonsense","0 days without degeneracy"]:
        message.content = "!reset_the_timer"
        await bot.process_commands(message)
        return

    if message.content.lower() in ["the timer","what's the time","!the_timer"]:
        message.content = "!the_timer"
        await bot.process_commands(message)
        return

    if message.channel.id==BOTS_CHANNEL_ID:
        if await canUseCommand(message,0,tellReason=False) and message.content.count("!")>1:
            for content in message.content.split("!"):
                if content.strip():
                    message.content="!"+content.strip()
                    await bot.process_commands(message)
        else:
            await bot.process_commands(message)



@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id==COLOR_CHOOSER_MESSAGE_ID:
        lookingAt="color"
    elif payload.message_id==IAM_MESSAGE_ID:
        lookingAt="iam"
    else:
        printLog("event","User reacted to other message")
        return

    # Ignore the bot reacting to the message
    if payload.user_id==bot.user.id:
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
    guild=bot.get_guild(payload.guild_id)
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


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id==COLOR_CHOOSER_MESSAGE_ID:
        lookingAt="color"
    elif payload.message_id==IAM_MESSAGE_ID:
        lookingAt="iam"
    else:
        return

    # Ignore the bot reacting to the message
    if payload.user_id==bot.user.id:
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
    guild=bot.get_guild(payload.guild_id)
    if guild is None:
        return
    member=guild.get_member(payload.user_id)
    role=guild.get_role(role_id)
    if member is None or role is None:
        return
    await member.remove_roles(role)





#move these into cog
@bot.command()
async def set_steam_id(self, ctx, id: int):
    senderID = ctx.author.id
    if ctx.channel.id == BOTS_CHANNEL_ID:
        account_id = id - 76561197960265728
        self.bot.user_data[str(senderID)]["steamID"] = str(account_id)
        self.bot.user_data[str(senderID)]["steamID64"] = str(id)
        await ctx.reply("Steam ID saved! Fetching your rank and most played heroes... " + chooseFaceFromCategory("concentrate"))
        result = await fetch_rank_from_api(id)
        if result:
            rank, division_tier = result
            self.bot.user_data[str(senderID)]["rank"] = rank
            await assign_rank_role(ctx.author, rank)
            await ctx.reply("Your rank has been automatically set to: **" + rank.capitalize() + " " + str(division_tier) + "** " + chooseFaceFromCategory("happy"))
        else:
            await ctx.reply("Couldn't fetch your rank automatically. Make sure your Steam profile is public and you have played ranked matches. You can set it manually with `!set_rank`.")
        heroes = await fetch_most_played(id)
        if heroes:
            top = heroes[0]
            self.bot.user_data[str(senderID)]["main"] = top["name"]
            await assign_hero_role(ctx.author, top["name"])
            heroes_str = ", ".join(f"**{h['name']}** ({h['matches']} games)" for h in heroes)
            await ctx.reply(f"Most played: {heroes_str}\nMain automatically set to **{top['name']}** " + chooseFaceFromCategory("happy"))

@bot.command()
async def update_rank(ctx):
    senderID = ctx.author.id
    if ctx.channel.id == BOTS_CHANNEL_ID:
        steam_id_64 = bot.user_data[str(senderID)].get("steamID64", "None")
        if steam_id_64 == "None" or not steam_id_64:
            await ctx.reply("You haven't set your Steam ID yet. Use `!set_steam_id <your_steamid64>` first.")
            return
        await ctx.reply("Fetching your latest rank... " + chooseFaceFromCategory("concentrate"))
        result = await fetch_rank_from_api(int(steam_id_64))
        if result:
            rank, division_tier = result
            bot.user_data[str(senderID)]["rank"] = rank
            await assign_rank_role(ctx.author, rank)
            await ctx.reply("Your rank has been updated to: **" + rank.capitalize() + " " + str(division_tier) + "** " + chooseFaceFromCategory("happy"))
        else:
            await ctx.reply("Couldn't fetch your rank. Make sure your Steam profile is public and you have played ranked matches.")

@bot.command()
async def profile(ctx, member: discord.Member = None):
    if ctx.channel.id != BOTS_CHANNEL_ID:
        return
    target = member or ctx.author
    senderID = str(target.id)
    if senderID not in bot.user_data:
        await ctx.reply(f"{target.display_name} hasn't registered yet. Use `!set_steam_id` first.")
        return

    data = bot.user_data[senderID]
    steam_id_64 = data.get("steamID64", "None")

    msg = await ctx.reply("Loading profile... " + chooseFaceFromCategory("concentrate"))

    rank_str = "Unknown"
    rank_color = discord.Color.blurple()
    if steam_id_64 != "None":
        rank_result = await fetch_rank_from_api(int(steam_id_64))
        if rank_result:
            rn, rt = rank_result
            rank_str = f"{rn.capitalize()} {rt}"
            rank_color = RANK_COLORS.get(rn, discord.Color.blurple())
            data["rank"] = rn

    heroes = []
    if steam_id_64 != "None":
        heroes = await fetch_most_played(int(steam_id_64), top_n=3) or []

    main = data.get("main", "None")
    embed = discord.Embed(
        title=f"⚔️  {target.display_name}'s Deadlock Profile",
        color=rank_color
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🏅  Rank", value=f"**{rank_str}**", inline=True)
    embed.add_field(name="🎮  Main", value=f"**{main}**", inline=True)
    embed.add_field(name="​", value="​", inline=False)

    if heroes:
        medals = ["🥇", "🥈", "🥉"]
        for i, h in enumerate(heroes):
            embed.add_field(
                name=f"{medals[i]}  {h['name']}",
                value=f"`{h['matches']}` games  •  `{h['winrate']}%` WR  •  `{h['kda']}` KDA",
                inline=False
            )

    embed.set_footer(text="Use the buttons below to set your main hero")

    view = None
    if target.id == ctx.author.id and heroes:
        view = MainPickerView(ctx.author, heroes)

    await msg.edit(content=None, embed=embed, view=view)


@tasks.loop(seconds=1)
async def tick():
    for i, (name,timerData) in enumerate(bot.timers.items()):
        timerTime=timerData["time"]
        if timerTime!=None:
            if timerData["paused"]:
                bot.timers[name]["time"]+=1
            curTime=time.time()//1
            timerTime=timerTime//1
            if timerTime-curTime==60:
                await bot.get_channel(BOTS_CHANNEL_ID).send("1 minute remaining on the "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"] timer.",delete_after=60)
            elif timerTime<=curTime:
                await bot.get_channel(BOTS_CHANNEL_ID).send("Moving people in category "+VOICE_CHANNEL_CAT_NAME_PREFIX+"["+name+"].",delete_after=60)
                for guild in bot.guilds:
                    category = discord.utils.get(guild.categories, name="["+name+"]")
                    TARGET=discord.utils.get(category.voice_channels, name="Deadlock ["+name+"]").id
                    SOURCES=[]
                    for other in category.voice_channels:
                        if other.id!=TARGET:
                            SOURCES.append(other.id)
                for channel in SOURCES:
                    people=[]
                    lane=bot.get_channel(channel)
                    if lane:
                        people=lane.members
                    if len(people)!=0:
                        for member in people:
                            try:
                                await member.move_to(bot.get_channel(TARGET))
                            except discord.Forbidden:
                                await bot.get_channel(BOTS_CHANNEL_ID).send("Can't move "+member.display_name)
                            except discord.HTTPException:
                                pass
                bot.timers[name]["timer"]=None


bot.startTimers={"A":11*60,"B":11*60}
bot.timers={"A":{"time":None},"B":{"time":None}}
bot.bootTime=time.time()//1
bot.version="0.8.2"
bot.versionSTR=""

bot.name="FUNLOCK BOT" #Not yet decided



bot.messageCD=MESSAGE_CD
bot.greetCD=GREET_CD
bot.degenTimer=deep_load_txt(BotPaths.degen_timer_file)

bot.user_data=deep_load_json(BotPaths.user_data_file)
idSTR="global"
if idSTR not in bot.user_data.keys():
    bot.user_data[idSTR]={}
    bot.user_data[idSTR]["main"]="None"
    bot.user_data[idSTR]["steamID"]="None"
    bot.user_data[idSTR]["steamID3"]="None"
    bot.user_data[idSTR]["steamID64"]="None"
    bot.user_data[idSTR]["rank"]="None"
    bot.user_data[idSTR]["lvl"]=1
    bot.user_data[idSTR]["XP"]=0
    bot.user_data[idSTR]["wins"]=0
if "money" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["money"]={}
    bot.user_data[idSTR]["money"]["unsecured"]=0
    bot.user_data[idSTR]["money"]["secured"]=0
if "items" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["items"]=[]
if "hidden" not in bot.user_data[idSTR].keys():
    bot.user_data[idSTR]["hidden"]={}
    bot.user_data[idSTR]["hidden"]["messageCD"]=0
    bot.user_data[idSTR]["hidden"]["greetMessageCD"]=0
if "interact" not in bot.user_data[idSTR]["hidden"].keys():
    bot.user_data[idSTR]["hidden"]["interact"]={}

bot.characters=load_txt(BotPaths.characters_file)
bot.characters=load_json(BotPaths.characters_file_json)
bot.maxLevel=bot.characters[list(bot.characters.keys())[0]]["maxLvl"]

bot.items=loadItemsProper(load_txt(BotPaths.items_file))
bot.map_graph=load_json(BotPaths.map_graph_file)

bot.ranks=load_json(BotPaths.ranks_file)

load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))



