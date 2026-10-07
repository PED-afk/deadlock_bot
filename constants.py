
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

#bot owner
ME=616710497378631709

#can use funlock bot role id
BOT_ROLE=1516075439347470437
MOD_ROLE=1515132970019848212

#in seconds
BOT_INTERACTION_TIMEOUT=60*15

BOT_SERVER_SPEC_NAME={
    FUNLOCK_SERVER_ID:"FUNLOCK BOT"
}
BOT_SECRET_NICKNAMES=["Remling"]


#greets and responses
ACCEPTED_GREETS=["hello","hi","good morning","good evening","good afternoon","hey","hey there","hoi","hoy"  ]
#empty str is intentional
GREET_RESPONSES=["Hello!","Hewwo!","","Hi!","Hiiiii!","Hoi!","Hoy!"]
GREET_SEARCH_LIMIT=10



COLOR_CHOOSER_MESSAGE_ID=1543703073992745011
COLOR_CHOOSER_MESSAGE_CONTENT="React to this message to set your name's color.\n You can only have 1."
COLORED_ROLES={
    "purple":{"id":1543693742031249418,"emoji":"🟣"},
    "blue":{"id":1535060305116401704,"emoji":"🔵"},
    "green":{"id":1543685911328460980,"emoji":"🟢"},
    "pink":{"id":1534677907358879765,"emoji":"🩷"},
    "yellow":{"id":1543685960292900884,"emoji":"🟡"},
    "orange":{"id":1543689973117489212,"emoji":"🟠"},
    "red":{"id":1543686317228167311,"emoji":"🔴"}
}

IAM_MESSAGE_ID=1548721180603842654
IAM_MESSAGE_CONTENT="What do you do?\nWhat notifications do you want?\nYou can choose more than 1.\n\n- If you usualy available to play with (you will be pinged by people looking for players): 🎮\n- If someone is loooking for players and you want to be pinged only if you appear as online: 👻\n- If you know programing: ⌨️\n- If you want to edit the bot's code(\*)(\*2): 🤖\n\n-# (*)We will periodically check this role to give access to the github repository; until we do use `!source` to get the active link to it.\n-# (*2)Getting this role won't necessarily mean you get access, we may deny your 'application'"
WHO_AM_I_ROLES={
    "programer":{
        "id":1543698321279946874,
        "emoji":"⌨️"
    },
    "regular_gamer":{
        "id":1530270967736041712,
        "emoji":"🎮"
    },
    "ping_if_online":{
        "id":1550424746720624640,
        "emoji":"👻"
    },
    "bot_coder_wannabe":{
        "id":1543929441225412608,
        "emoji":"🤖"
    }
}

WARNING_MESSAGE_IN_NAMETAG_CHANNEL="Warnig!!!\nBefore you add a reaction, check if the @ is online! If not wait until if it is.\nIf you haven't recieved the roles you wanted, remove and read your reactions (when the bot is online).\n\n-# The bot may appear online right after it shuts down or crashes. Check the # channel for shutdown and startup messages."
WARNING_MESSAGE_IN_NAMETAG_CHANNEL_ID=1553357812409704489


SUGGESTIONS_NEW_TAG_ID=1544065933948223558

SUGGESTIONS_REJ_TAG_ID=1544065901794426981
SUGGESTIONS_ACC_TAG_ID=1544065868537794660
SUGGESTIONS_CANT_TAG_ID=1545425498581110846


HANDPICKED_SUP_USER_IDS=[
    534796790105505794 #clever
]
AUTODELETE_TRESHOLD=2.5
AUTODELETE_TIME_SECONDS=60*60*0.16 #~10 minutes
MAX_MODERATABLE_MESSAGE_AGE_HOUR=12
MIN_TIME_BETWEEN_SHH_UPDATE_SECONDS=60*5 #5 minutes


DEGEN_TIMER_RESET_MESSAGES=["reset the timer","reset timer","!reset_the_timer","0 days without degenerate nonsense","0 days without degeneracy","🕰️","⏰","🕐","🕙","🕥","🕚","🕦","🕛","🕧","🕜","🕑","🕝","🕒","🕞","🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢","🕗","🕣","🕘","🕤","⏱️","⏲️","⌚"]
DEGEN_TIMER_ASK_MESSAGES=["the timer","what's the time","!the_timer"]

THANKING_MESSAGES=["thank you!","thank you","thanks!","thanks"]


class ROLES():
    BOT_PROGRAMMER=1523561168956817578
    GITHUB_HELPER=1542983727632752740
    GITHUB_HELPER_APLICANT=1543929441225412608
    BOT_ROLE_NOT_AUTO_CREATED=1544310435451248660
    
class CHANNEL_IDS():
    FLOOR_PLAN_CHANNEL_ID=1554145604840456222
    RULES_CHANNEL_ID=1526999395092922469
    ROLE_CHANNEL_ID=1543701162581168228
        
    BOTS_CHANNEL_ID=1515333724269445270
    BOT_DEBUG_CHANNEL=1524176375903420466
    LOUNGE_CHANNEL_ID=1510049700416327753
    
    JUST_ZIPLINE_ID=1520781404315848736
    PA_ID=1535310773684019201
    LOBBY_CODES_ID=1515295871028432977
    CURIOSITY_ID=1544085021156184214
    SEMINAR_ROOM_ID=1521993492572799037
    PROJECTOR_ID=1515343404383473775
    PROJECT_SHARE=1523560126806622298
    SUGGESTIONS_CHANNEL_ID=1544060319263883324
    STAT_TRACKER_CHANNEL_ID=1515053044813791282
    

FLOOR_PLAN_MESSAGE=("Here are the channels and what they are used for!\n"
                    "- Reception\n"
                    "  - #0#  This is where you can greet the newcomers.\n"
                    "  - #1#  Here you can find the rules you must follow on this server.\n"
                    "  - #2#  This is where you are right now, and where you can read where to find what.\n"
                    "  - #3#  Choose your name color and roles here, check it out to learn more.\n"
                    "  - #4#  Here you can read about server wide announcements.\n"
                    "- The Hideout\n"
                    "  - #5# Talk About all kind of things\n"
                    "  - #6# When you want to play with others this is where you put your in game lobby codes.\n"
                    "  - #7# Share your builds.\n"
                    "  - #8# You seek knoledge or want to share some of yours? You can do it here.\n"
                    "  - #9# You can share your videos, clips, and pictures here.\n"
                    "  - #10# Share whatever you made.\n"
                    "  - #11# Suggestions/changes about the server or our bot go here.\n"
                    "- Miss Shelly's Workshop\n"
                    "  - #12# Commands for our dedicadet bot and the outputs from those commands. Use `!help_me` to learn more.\n"
                    "  - #13# Deadlock stat tracker bot and it's commands.\n"
                    )

FLOOR_PLAN_MESSAGE_ID=1554149941826551850


RULES_MESSAGE=("1. Good Vibes. Positive coms. No bitching. It's a game, Have **`FUN`**!\n"
                "\n"
                "2. Treat everyone with respect. Absolutely no harassment, witch hunting, sexism, racism, homophobia or hate speech will be tolerated.\n"
                "\n"
                "3. No spam or self-promotion (server invites, advertisements etc) without permission from a staff member. This includes DMing fellow members.\n"
                "\n"
                "4. No age-restricted or obscene content. This includes text, images or links featuring nudity, sex, hard violence or other disturbing graphic content.\n"
                "\n"
                "5. Use the proper channels.\n"
                )
RULES_MESSAGE_ID=1554150097887957173


PRIVATE_MESSAGE_CONTENT=(
    "###Hello friend! Welcome to the Funlock server!"
    "\n\tI am the server's dedicated bot!"
    "\n"
    "\n## What you should do:"
    "\n- Please read our rules in #0#!"
    "\n- After that, visit #1# to select a name color for yourself and set when you want to be pinged!"
    "\n-#   We would really **appreciate** it if you **didn't** skip out on this. #f#"
    "\n- Finally check out the #2# to see what your options are."
    "\n"
    "\n# -# Warning:"
    "\n-# - (This is an automated message)"
    "\n-# - If you notice any spelling mistakes or bad formatting please take a screenshot of this message,"
    " send it to the #3# channel with the `BUG Report` tag applied and describe the problem."
    "\n"
    "\n### Thank you for your time and again Welcome!"
    )


MAX_MONEY_SECURE_AFTER_GAME=500
