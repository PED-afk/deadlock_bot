


from constants import APP_NAME

from pathlib import Path
from platformdirs import user_data_dir
import json
import time
from debug import printLog




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

def deep_load_txt(fileName:str,appName:str=""):
    """
    !!!WARNING!!!\n
    If the file doesn't exist this funtion will return the current time using `time.time()`
    unless a custom appName is given in which case it will return -1
    """

    fallback=0
    if appName=="":
        data_dir = Path(user_data_dir(APP_NAME))
    else:
        data_dir = Path(user_data_dir(appName))
        fallback=1
    file_path = data_dir / fileName

    # Load
    if file_path.exists():
        with open(file_path,"r") as f:
            data=f.readline().strip()
    else:
        printLog("error",f"File doesn't exist. {file_path}")
        if fallback==0:
            data = time.time()
        else:
            return -1
    return data

def deep_save_txt(name:str,data:str,appName:str=""):
    if appName=="":
        data_dir = Path(user_data_dir(APP_NAME))
    else:
        data_dir = Path(user_data_dir(appName))
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / name
    file_path.write_text(data, encoding="utf-8")

    

