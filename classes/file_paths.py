
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

    characters_file_json = BASE / "characters.json"
    items_file = BASE / "items.txt"
    map_graph_file = BASE / "map_graph.json"

    face_file = BASE / "faces.json"
    ranks_file=BASE / "ranks.json"

    sounds_folder=BASE / "sounds"
    class vcSounds():
        SILLY=Path("voicechat") / "silly.mp3"
        SILLYER=Path("voicechat") / "silly2.mp3"
        FIH=Path("voicechat") / "fish_long.mp3"
        FISH=Path("voicechat") / "FISH.mp3"
        PORTAL=Path("voicechat") / "portal.mp3"
        PING=Path("voicechat") / "dc_ping.mp3"
        TEST="placeholder.mp3"

        ELEVATOR0=Path("voicechat") / "elevator_music0.mp3"
        ELEVATOR1=Path("voicechat") / "elevator_music1.mp3"
        ELEVATORLONG=Path("voicechat") / "elevator_music1long.mp3"

        SILENCE=Path("voicechat") / "silence.mp3"

    pfp_folder=BASE / "images" / "pfp"

    credits_file=BASE / "data" / "3rd_party_credits.json"

    lookForUpdates=BASE / "update.txt"
    
    autoMessage_file=BASE / "data" / "send_these_at_time.json"
    autoMessage_file_gitignored=BASE / "data" / "send_these_at_time_gitignored.json"
