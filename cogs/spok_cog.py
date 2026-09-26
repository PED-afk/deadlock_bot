
import discord
from discord.ext import commands, tasks
import aiohttp

from own_utils import chooseFaceFromCategory
from constants import BOTS_CHANNEL_ID, HERO_ID_MAP, RANK_NAMES, RANK_COLORS

from classes.file_paths import BotPaths
from classes.bot_faces import Faces

#stuff "made" by spooks
#moved here so main file is cleaner

class SpokCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot


    async def fetch_hero_id_to_name(self) -> dict[int, str]:
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

    async def fetch_most_played(self,steam_id_64: int, top_n: int = 3) -> list[dict] | None:
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
                    hero_map = await self.fetch_hero_id_to_name()
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

    async def assign_hero_role(self,member: discord.Member, hero_name: str):
        guild = member.guild
        all_heroes = list(self.bot.characters.keys())
        existing = [r for r in member.roles if r.name in all_heroes]
        if existing:
            await member.remove_roles(*existing, reason="Hero role update")
        role = discord.utils.get(guild.roles, name=hero_name)
        if role is None:
            role = await guild.create_role(name=hero_name, reason="Auto-created hero role")
        await member.add_roles(role, reason="Main hero assigned")

    class MainPickerView(discord.ui.View):
        def __init__(self, bot, author: discord.Member, heroes: list[dict]):
            super().__init__(timeout=60)
            self.bot=bot
            self.author = author
            for h in heroes:
                btn = discord.ui.Button(label=h["name"], style=discord.ButtonStyle.primary)
                async def callback(interaction: discord.Interaction, hero=h):
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message("These aren't your buttons!", ephemeral=True)
                        return
                    senderID = str(interaction.user.id)
                    self.bot.user_data[senderID]["main"] = hero["name"]
                    await self.assign_hero_role(interaction.user, hero["name"])
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


    @commands.command()
    async def set_steam_id(self, ctx, id: int):
        senderID = ctx.author.id
        if ctx.channel.id == BOTS_CHANNEL_ID:
            account_id = id - 76561197960265728
            self.bot.user_data[str(senderID)]["steamID"] = str(account_id)
            self.bot.user_data[str(senderID)]["steamID64"] = str(id)
            await ctx.reply("Steam ID saved! Fetching your rank and most played heroes... " + chooseFaceFromCategory("concentrate"))
            result = await self.fetch_rank_from_api(id)
            if result:
                rank, division_tier = result
                self.bot.user_data[str(senderID)]["rank"] = rank
                await self.assign_rank_role(ctx.author, rank)
                await ctx.reply("Your rank has been automatically set to: **" + rank.capitalize() + " " + str(division_tier) + "** " + chooseFaceFromCategory("happy"))
            else:
                await ctx.reply("Couldn't fetch your rank automatically. Make sure your Steam profile is public and you have played ranked matches. You can set it manually with `!set_rank`.")
            heroes = await self.fetch_most_played(id)
            if heroes:
                top = heroes[0]
                self.bot.user_data[str(senderID)]["main"] = top["name"]
                await self.assign_hero_role(ctx.author, top["name"])
                heroes_str = ", ".join(f"**{h['name']}** ({h['matches']} games)" for h in heroes)
                await ctx.reply(f"Most played: {heroes_str}\nMain automatically set to **{top['name']}** " + chooseFaceFromCategory("happy"))

    @commands.command()
    async def update_rank(self,ctx):
        senderID = ctx.author.id
        if ctx.channel.id == BOTS_CHANNEL_ID:
            steam_id_64 = self.bot.user_data[str(senderID)].get("steamID64", "None")
            if steam_id_64 == "None" or not steam_id_64:
                await ctx.reply("You haven't set your Steam ID yet. Use `!set_steam_id <your_steamid64>` first.")
                return
            await ctx.reply("Fetching your latest rank... " + chooseFaceFromCategory("concentrate"))
            result = await self.fetch_rank_from_api(int(steam_id_64))
            if result:
                rank, division_tier = result
                self.bot.user_data[str(senderID)]["rank"] = rank
                await self.assign_rank_role(ctx.author, rank)
                await ctx.reply("Your rank has been updated to: **" + rank.capitalize() + " " + str(division_tier) + "** " + chooseFaceFromCategory("happy"))
            else:
                await ctx.reply("Couldn't fetch your rank. Make sure your Steam profile is public and you have played ranked matches.")

    @commands.command()
    async def profile(self,ctx, member: discord.Member = None):
        if ctx.channel.id != BOTS_CHANNEL_ID:
            return
        target = member or ctx.author
        senderID = str(target.id)
        if senderID not in self.bot.user_data:
            await ctx.reply(f"{target.display_name} hasn't registered yet. Use `!set_steam_id` first.")
            return

        data = self.bot.user_data[senderID]
        steam_id_64 = data.get("steamID64", "None")

        msg = await ctx.reply("Loading profile... " + chooseFaceFromCategory("concentrate"))

        rank_str = "Unknown"
        rank_color = discord.Color.blurple()
        if steam_id_64 != "None":
            rank_result = await self.fetch_rank_from_api(int(steam_id_64))
            if rank_result:
                rn, rt = rank_result
                rank_str = f"{rn.capitalize()} {rt}"
                rank_color = RANK_COLORS.get(rn, discord.Color.blurple())
                data["rank"] = rn

        heroes = []
        if steam_id_64 != "None":
            heroes = await self.fetch_most_played(int(steam_id_64), top_n=3) or []

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
            view = self.MainPickerView(self.bot,ctx.author, heroes)

        await msg.edit(content=None, embed=embed, view=view)




async def setup(bot):
    await bot.add_cog(SpokCog(bot))