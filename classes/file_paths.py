
from constants import BASE

class BotPaths():
    hotboot_file = BASE / "hotBoot.txt"
    restart_file = BASE / "restart.txt"
    user_data_path = BASE / "user_data.json"
    pause_file = BASE / "pauseTimes.txt"

    characters_file = BASE / "characters.txt"
    characters_file_json = BASE / "characters.json"
    items_file = BASE / "items.txt"
    map_graph_file = BASE / "map_graph.json"

    face_file = BASE / "faces.json"
    ranks_file=BASE / "ranks.json"

    sounds_folder=BASE / "sounds"

    pfp_folder=BASE / "images" / "pfp"

    credits_file=BASE / "data" / "3rd_party_credits.json"
