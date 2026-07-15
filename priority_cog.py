"""
Drop-in cog: team pick priority for Deadlock.

Usage — in your main bot file, add ONE line after `bot` is created:
    asyncio.run(bot.load_extension("priority_cog"))   # if using __main__
    # — OR —
    await bot.load_extension("priority_cog")          # inside an async on_ready / setup_hook

Slash commands added:
    /priority set   <pick1> [pick2] [pick3] [pick4] [pick5]
    /priority show
    /priority clear
    /priority reset-team   (requires Manage Guild or admin)
"""

import asyncio
import io
import json
from pathlib import Path

import aiohttp
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# ── paths ────────────────────────────────────────────────────────────────────
BASE         = Path(__file__).parent
DB_PATH      = BASE / "priority.db"
CACHE_PATH   = BASE / "hero_cache.json"
STATIC_PATH  = BASE / "heroes_static.json"

# ── visual constants ──────────────────────────────────────────────────────────
THUMB_W, THUMB_H = 80, 80
LABEL_H          = 18          # px below each thumbnail for hero name
NAME_COL_W       = 160         # px for the Discord display-name column
MAX_PICKS        = 5
ROW_H            = THUMB_H + LABEL_H + 16   # padding
TOP_PAD          = 14
LEFT_PAD         = 14
BG_COLOR         = (18, 18, 24)
ROW_ALT          = (24, 24, 32)
ACCENT           = (90, 180, 255)
TEXT_COLOR       = (220, 220, 220)
DIM_COLOR        = (100, 100, 120)
EMPTY_COLOR      = (40, 40, 55)

# ── hero cache ────────────────────────────────────────────────────────────────
_hero_cache: list[dict] = []   # [{name, icon_url}, ...]

async def refresh_hero_cache() -> None:
    global _hero_cache
    url = "https://api.deadlock-api.com/v1/heroes"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200:
                    raise RuntimeError(f"HTTP {r.status}")
                data = await r.json()
        heroes = []
        for h in data:
            name = h.get("name") or h.get("display_name") or ""
            if not name:
                continue
            icon = (
                h.get("images", {}).get("icon_hero_card")
                or h.get("images", {}).get("portrait")
                or h.get("icon_url")
                or h.get("portrait_url")
                or ""
            )
            heroes.append({"name": name, "icon_url": icon})
        heroes.sort(key=lambda x: x["name"])
        _hero_cache = heroes
        CACHE_PATH.write_text(json.dumps(heroes, indent=2))
        print(f"[priority_cog] hero cache refreshed: {len(heroes)} heroes", flush=True)
    except Exception as e:
        print(f"[priority_cog] hero refresh failed: {e}", flush=True)
        if CACHE_PATH.exists():
            _hero_cache = json.loads(CACHE_PATH.read_text())
            print(f"[priority_cog] loaded {len(_hero_cache)} heroes from disk cache", flush=True)
        elif STATIC_PATH.exists():
            data = json.loads(STATIC_PATH.read_text())
            names = data.get("deadlock_characters", {}).get("active_heroes", [])
            _hero_cache = [{"name": n, "icon_url": ""} for n in names]
            print(f"[priority_cog] loaded {len(_hero_cache)} heroes from static fallback list", flush=True)

def hero_names() -> list[str]:
    return [h["name"] for h in _hero_cache]

def icon_url_for(name: str) -> str:
    for h in _hero_cache:
        if h["name"].lower() == name.lower():
            return h["icon_url"]
    return ""

# ── database ──────────────────────────────────────────────────────────────────
async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS priorities (
                guild_id   INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                picks      TEXT    NOT NULL DEFAULT '[]',
                updated_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        await db.commit()

async def db_set_picks(guild_id: int, user_id: int, picks: list[str]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO priorities (guild_id, user_id, picks, updated_at)
            VALUES (?, ?, ?, strftime('%s','now'))
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                picks      = excluded.picks,
                updated_at = excluded.updated_at
        """, (guild_id, user_id, json.dumps(picks)))
        await db.commit()

async def db_clear_picks(guild_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM priorities WHERE guild_id=? AND user_id=?",
            (guild_id, user_id)
        )
        await db.commit()

async def db_reset_team(guild_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM priorities WHERE guild_id=?", (guild_id,))
        await db.commit()

async def db_get_team(guild_id: int) -> list[tuple[int, list[str]]]:
    """Returns [(user_id, picks), ...] ordered by updated_at."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id, picks FROM priorities WHERE guild_id=? ORDER BY updated_at",
            (guild_id,)
        ) as cur:
            rows = await cur.fetchall()
    return [(r[0], json.loads(r[1])) for r in rows]

# ── image generation ──────────────────────────────────────────────────────────
async def _fetch_image(url: str, session: aiohttp.ClientSession) -> Image.Image | None:
    if not url:
        return None
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as r:
            if r.status != 200:
                return None
            data = await r.read()
        return Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None

def _make_placeholder() -> Image.Image:
    img = Image.new("RGBA", (THUMB_W, THUMB_H), EMPTY_COLOR)
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, THUMB_W - 3, THUMB_H - 3], outline=DIM_COLOR, width=1)
    return img

def _try_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ["DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()

async def build_priority_image(
    guild: discord.Guild,
    rows: list[tuple[int, list[str]]],
) -> bytes:
    """Returns PNG bytes of the priority board."""
    font_name  = _try_font(13)
    font_hero  = _try_font(10)
    font_empty = _try_font(10)

    # resolve display names
    members: dict[int, str] = {}
    for uid, _ in rows:
        try:
            m = guild.get_member(uid) or await guild.fetch_member(uid)
            members[uid] = m.display_name
        except Exception:
            members[uid] = str(uid)

    # download all portrait thumbnails
    all_hero_names = list({pick for _, picks in rows for pick in picks})
    icon_map: dict[str, Image.Image] = {}
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[_fetch_image(icon_url_for(n), session) for n in all_hero_names],
            return_exceptions=True
        )
    for name, img in zip(all_hero_names, results):
        if isinstance(img, Image.Image):
            icon_map[name] = img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        else:
            icon_map[name] = _make_placeholder()

    n_rows = max(len(rows), 1)
    img_w  = LEFT_PAD + NAME_COL_W + MAX_PICKS * (THUMB_W + 8) + LEFT_PAD
    img_h  = TOP_PAD + n_rows * ROW_H + TOP_PAD

    canvas = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw   = ImageDraw.Draw(canvas)

    # header line
    draw.text((LEFT_PAD, 4), "Team Priority Picks", font=font_name, fill=ACCENT)

    for row_i, (uid, picks) in enumerate(rows):
        y0 = TOP_PAD + row_i * ROW_H
        # alternating row bg
        if row_i % 2 == 1:
            draw.rectangle([0, y0, img_w, y0 + ROW_H], fill=ROW_ALT)

        # display name
        name_text = members.get(uid, str(uid))
        if len(name_text) > 18:
            name_text = name_text[:17] + "…"
        draw.text(
            (LEFT_PAD, y0 + (THUMB_H // 2) - 6),
            name_text, font=font_name, fill=TEXT_COLOR
        )

        # divider
        draw.line(
            [(LEFT_PAD + NAME_COL_W - 8, y0 + 6), (LEFT_PAD + NAME_COL_W - 8, y0 + ROW_H - 6)],
            fill=DIM_COLOR, width=1
        )

        # hero thumbnails
        for col_i in range(MAX_PICKS):
            x0 = LEFT_PAD + NAME_COL_W + col_i * (THUMB_W + 8)
            ty = y0 + 6

            if col_i < len(picks):
                hero_name = picks[col_i]
                thumb = icon_map.get(hero_name, _make_placeholder())
                canvas.paste(thumb, (x0, ty), thumb if thumb.mode == "RGBA" else None)
                # priority number badge
                draw.ellipse([x0, ty, x0 + 16, ty + 16], fill=(0, 0, 0, 180))
                draw.text((x0 + 4, ty + 2), str(col_i + 1), font=font_empty, fill=ACCENT)
                # hero name label
                label = hero_name if len(hero_name) <= 11 else hero_name[:10] + "…"
                draw.text(
                    (x0 + THUMB_W // 2, ty + THUMB_H + 2),
                    label, font=font_hero, fill=TEXT_COLOR, anchor="mt"
                )
            else:
                # empty slot
                draw.rectangle([x0, ty, x0 + THUMB_W, ty + THUMB_H], fill=EMPTY_COLOR)
                draw.rectangle([x0, ty, x0 + THUMB_W, ty + THUMB_H], outline=DIM_COLOR, width=1)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

# ── cog ───────────────────────────────────────────────────────────────────────
class PriorityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    priority = app_commands.Group(name="priority", description="Team hero pick priority")

    # autocomplete helper
    async def hero_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        lower = current.lower()
        matches = [n for n in hero_names() if lower in n.lower()]
        return [app_commands.Choice(name=n, value=n) for n in matches[:25]]

    # /priority set
    @priority.command(name="set", description="Set your hero pick priority (up to 5)")
    @app_commands.describe(
        pick1="1st priority hero",
        pick2="2nd priority hero",
        pick3="3rd priority hero",
        pick4="4th priority hero",
        pick5="5th priority hero",
    )
    @app_commands.autocomplete(
        pick1=hero_autocomplete,
        pick2=hero_autocomplete,
        pick3=hero_autocomplete,
        pick4=hero_autocomplete,
        pick5=hero_autocomplete,
    )
    async def priority_set(
        self,
        interaction: discord.Interaction,
        pick1: str,
        pick2: str | None = None,
        pick3: str | None = None,
        pick4: str | None = None,
        pick5: str | None = None,
    ):
        await interaction.response.defer(thinking=True)
        picks = [p for p in [pick1, pick2, pick3, pick4, pick5] if p]
        valid = hero_names()
        bad   = [p for p in picks if p not in valid]
        if bad:
            await interaction.followup.send(
                f"Unknown hero(es): {', '.join(bad)}. Use autocomplete to pick valid heroes.",
                ephemeral=True
            )
            return

        await db_set_picks(interaction.guild_id, interaction.user.id, picks)

        rows = await db_get_team(interaction.guild_id)
        img  = await build_priority_image(interaction.guild, rows)
        file = discord.File(io.BytesIO(img), filename="priority.png")
        embed = discord.Embed(
            title="Team Priority Picks",
            color=discord.Color.from_rgb(90, 180, 255)
        )
        embed.set_image(url="attachment://priority.png")
        embed.set_footer(text=f"Updated by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed, file=file)

    # /priority show
    @priority.command(name="show", description="Show the whole team's current priority lists")
    async def priority_show(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        rows = await db_get_team(interaction.guild_id)
        if not rows:
            await interaction.followup.send("No priorities set yet. Use `/priority set` to add yours.", ephemeral=True)
            return
        img  = await build_priority_image(interaction.guild, rows)
        file = discord.File(io.BytesIO(img), filename="priority.png")
        embed = discord.Embed(
            title="Team Priority Picks",
            color=discord.Color.from_rgb(90, 180, 255)
        )
        embed.set_image(url="attachment://priority.png")
        await interaction.followup.send(embed=embed, file=file)

    # /priority clear
    @priority.command(name="clear", description="Clear your own priority list")
    async def priority_clear(self, interaction: discord.Interaction):
        await db_clear_picks(interaction.guild_id, interaction.user.id)
        await interaction.response.send_message("Your priority list has been cleared.", ephemeral=True)

    # /priority reset-team
    @priority.command(name="reset-team", description="Wipe all priority lists for this server")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def priority_reset_team(self, interaction: discord.Interaction):
        await db_reset_team(interaction.guild_id)
        await interaction.response.send_message("All priority lists reset for this server.", ephemeral=True)

    @priority_reset_team.error
    async def reset_team_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("You need **Manage Server** permission for that.", ephemeral=True)


# ── setup hook (called by bot.load_extension) ─────────────────────────────────
async def setup(bot: commands.Bot) -> None:
    await init_db()
    await refresh_hero_cache()
    cog = PriorityCog(bot)
    await bot.add_cog(cog)
    # register the slash command group with the tree
    bot.tree.add_command(cog.priority)
    print("[priority_cog] loaded", flush=True)
