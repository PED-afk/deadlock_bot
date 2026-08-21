
import discord
from pathlib import Path

BASE = Path(__file__).parent

RANK_NAMES = [
    "initiate", "seeker", "alchemist", "arcanist", "ritualist",
    "emissary", "archon", "oracle", "phantom", "ascendant", "eternus"
]

RANK_COLORS = {
    "initiate":   discord.Color.from_rgb(180, 180, 180),
    "seeker":     discord.Color.from_rgb(150, 30, 30),
    "alchemist":  discord.Color.from_rgb(50, 120, 200),
    "arcanist":   discord.Color.from_rgb(40, 140, 60),
    "ritualist":  discord.Color.from_rgb(160, 90, 40),
    "emissary":   discord.Color.from_rgb(180, 40, 40),
    "archon":     discord.Color.from_rgb(120, 50, 180),
    "oracle":     discord.Color.from_rgb(160, 110, 50),
    "phantom":    discord.Color.from_rgb(180, 180, 190),
    "ascendant":  discord.Color.from_rgb(210, 170, 50),
    "eternus":    discord.Color.from_rgb(0, 210, 200),
}

HERO_ID_MAP = {
    1: "Infernus", 2: "Seven", 3: "Vindicta", 4: "Lady Geist", 6: "Abrams",
    7: "Wraith", 8: "McGinnis", 10: "Paradox", 11: "Dynamo", 12: "Kelvin",
    13: "Haze", 14: "Bebop", 15: "Ivy", 17: "Warden", 18: "Viscous",
    19: "Yamato", 20: "Mo & Krill", 25: "Shiv", 27: "Pocket", 31: "Mirage",
    35: "Calico", 50: "Holliday", 52: "Grey Talon", 53: "Lash", 55: "Sinclair",
    56: "Viper", 57: "Wraith", 58: "Dynamo", 60: "Magician", 61: "Trapper",
    62: "Nano", 63: "Fathom", 64: "Slork", 70: "Viscous", 71: "Yamato",
    80: "Kali", 81: "The Doorman",
}


APP_NAME="FUNLOCK_BOT"

MESSAGE_CD=60*60*0.1  #6 minutes
GREET_CD=60*60*12     #12 hours

VOICE_CHANNEL_CAT_NAME_PREFIX="Standard Matches "

#dc_ids
#server
FUNLOCK_SERVER_ID=1510049699695165471

#users
ME=616710497378631709
BOT_ROLE=1516075439347470437

#channel(s)
BOTS_CHANNEL_ID=1515333724269445270
BOT_DEBUG_CHANNEL=1524176375903420466

#in seconds
BOT_INTERACTION_TIMEOUT=60*15

BOT_SECRET_NICKNAMES=["Remling"]







