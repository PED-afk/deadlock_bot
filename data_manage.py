


from constants import APP_NAME

from pathlib import Path
from platformdirs import user_data_dir
import json
import time




def save_json(path:str,data:dict):
    with open(path,"w", encoding="utf-8") as f:
        return json.dump(data,f,indent=4,ensure_ascii=False)
    
def load_json(filePath:str):
    with open(filePath,"r", encoding="utf-8") as f:
        return json.load(f)

def deep_save_json(name:str,data:dict):
    data_dir = Path(user_data_dir(APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / name
    file_path.write_text(json.dumps(data), encoding="utf-8")

def deep_load_json(fileName:str):
    data_dir = Path(user_data_dir(APP_NAME))
    file_path = data_dir / fileName

    # Load
    if file_path.exists():
        data = json.loads(file_path.read_text(encoding="utf-8"))
    else:
        data = {}
    return data



    

def load_txt(filePath:str):
    contents=[]
    with open(filePath,"r") as f:
        line=f.readline().strip()
        while line:
            contents.append(line)
            line=f.readline().strip()
    return contents

def deep_load_txt(fileName:str):
    data_dir = Path(user_data_dir(APP_NAME))
    file_path = data_dir / fileName

    # Load
    if file_path.exists():
        with open(file_path,"r") as f:
            data=f.readline().strip()
    else:
        data = time.time()
    return data

def deep_save_txt(name:str,data:dict):
    data_dir = Path(user_data_dir(APP_NAME))
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / name
    file_path.write_text(data, encoding="utf-8")

    

