
from constants import BASE
from pathlib import Path

class BotPaths():
    hotboot_file = BASE / "hotBoot.txt"
    restart_file = BASE / "restart.txt"
    update_check_file= BASE / "update_check.txt"
    
    user_data_file = "user_data.json"
    user_data_path = BASE / user_data_file

    pause_file = BASE / "pauseTimes.txt"

    degen_timer_file="degen_timer.txt"
    degen_timer_path=BASE / degen_timer_file

    #characters_file = BASE / "characters.txt"
    characters_file_json = BASE / "characters.json"
    items_file = BASE / "items.txt"
    map_graph_file = BASE / "map_graph.json"

    face_file = BASE / "faces.json"
    ranks_file=BASE / "ranks.json"

    sounds_folder=BASE / "sounds"
    class vcSounds():
        SILLY=Path("voicechat" / "silly(128k).pcm")
        SILLYER=Path("voicechat" / "sillyer(128k).pcm")
        FIH=Path("voicechat" / "FIH(128k).pcm")
        FISH=Path("voicechat" / "FISH.pcm")
        PORTAL=Path("voicechat" / "portal.pcm")
        PING=Path("voicechat" / "dc_ping.pcm")

    pfp_folder=BASE / "images" / "pfp"

    credits_file=BASE / "data" / "3rd_party_credits.json"

    lookForUpdates=BASE / "update.txt"
    
    autoMessage_file=BASE / "data" / "send_these_at_time.json"
    autoMessage_file_gitignored=BASE / "data" / "send_these_at_time_gitignored.json"
