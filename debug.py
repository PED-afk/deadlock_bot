


import datetime
import os
#import traceback
from pathlib import Path
import shutil
from discord.ext import commands
import inspect

from constants import BOT_DEBUG_CHANNEL, BASE

class Colors:
    """ ANSI color codes """
    BLACK="\033[0;30m"
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    BROWN="\033[0;33m"
    BLUE="\033[0;34m"
    PURPLE="\033[0;35m"
    CYAN="\033[0;36m"
    LIGHT_GRAY="\033[0;37m"
    DARK_GRAY="\033[1;30m"
    LIGHT_RED="\033[1;31m"
    LIGHT_GREEN="\033[1;32m"
    YELLOW="\033[1;33m"
    LIGHT_BLUE="\033[1;34m"
    LIGHT_PURPLE="\033[1;35m"
    LIGHT_CYAN="\033[1;36m"
    LIGHT_WHITE="\033[1;37m"

    BOLD="\033[1m"
    FAINT="\033[2m"
    ITALIC="\033[3m"
    UNDERLINE="\033[4m"
    BLINK="\033[5m"
    NEGATIVE="\033[7m"
    CROSSED="\033[9m"

    END="\033[0m"


def setupFolders():
    ROOT_PATH=str(BASE)
    folder=Path(ROOT_PATH+"\\debug")
    folder.mkdir(parents=True, exist_ok=True)
    folder=Path(ROOT_PATH+"\\debug\\crash_reports")
    folder.mkdir(parents=True, exist_ok=True)
    folder=Path(ROOT_PATH+"\\debug\\logs")
    folder.mkdir(parents=True, exist_ok=True)
    folder=Path(ROOT_PATH+"\\debug\\logs\\log_errors")
    folder.mkdir(parents=True, exist_ok=True)

def writeLog(type:str, content:any, fileName:str, addNumber:bool=True, addDate:bool=True, writeType:str="w", fromFile:str="UNKNOWN", fromFunc:str="UNKNOWN"):
    """
        type: "crash"/"error", "log" ("log_e" is not for you)\n
        content: what to write into the file (may be anything, if not supported: will be)\n
        fileName: the name of the file !!!Without the extention!!!\n
        addNumber: add 0,1,2,3,.. to end of file (can only write; can't append) (can only add number or date)\n
        addDate: add date and time at end of file (can only add number or date)\n
        writeType: "w", "a"\n
        fromFile: please include file name where this log originates from, for easier trace\n
        fromFunc: please include function name where this log originates from, for easier trace\n
    """
    if content==None:
        return
    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))
    folderPath=ROOT_PATH
    fileExtention=".txt"
    if type=="crash" or type=="error":
        folderPath+="\\debug\\crash_reports"
        fileExtention="txt"
    elif type=="log":
        folderPath+="\\debug\\logs"
        fileExtention="log"
    elif type=="log_e":
        folderPath+="\\debug\\logs\\log_errors"
        fileExtention="log"
    else:
        writeLog("log_e",f"Log with unknown type from: {fromFile}; {fromFunc}\nWith type: {type}","LogError",True,False,"w","debug.py","writeLog")
        return


    if addNumber:
        folder=Path(folderPath)
        folder.mkdir(exist_ok=True)
        i=0
        while True:
            filename=f"{fileName}{i}.{fileExtention}"
            filepath=folder / filename
            if not filepath.exists():
                if isinstance(content,list):
                    filepath.write_text("\n".join(str(i) for i in content)+"\nFrom file: "+fromFile+"; From function: "+fromFunc)
                else:
                    filepath.write_text(content+"\nFrom file: "+fromFile+"; From function: "+fromFunc)
                break
            i += 1
        return
    if addDate:
        fullPath=folderPath+"\\"+fileName+str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+"."+fileExtention
        with open(fullPath,writeType) as f:
            f.write(content)
            f.write("\n")
            f.write(fromFile)
            f.write("; ")
            f.write(fromFunc)

def printLog(type:str, content:any, colorAll:bool=False):
    """

        type can also be the function the print is from
    """
    extra=''
    if type=="warning" or type=="error":
        extra=Colors.RED
    elif type=="debug":
        extra=Colors.YELLOW
    elif type=="debug2":
        extra=Colors.BROWN
    elif type=="log":
        extra=Colors.CYAN
    elif type=="info":
        extra=Colors.BLUE
    extra+=Colors.BOLD
    #print(extra+f"[{type.upper()}]"+(Colors.END if not colorAll else "")+f"  {content}"+Colors.END,flush=True)
    fromFunction = inspect.currentframe().f_back.f_code.co_name
    print(extra+f"[{type.upper()}]"+f" [{fromFunction.upper()}]"+(Colors.END if not colorAll else "")+f"  {content}"+(Colors.END if colorAll else ""),flush=True)


async def printLogToDc(bot:commands.Bot,type:str, content:str):
    """

        type can also be the function the print is from
    """
    
    fromFunction = inspect.currentframe().f_back.f_code.co_name
    await bot.get_channel(BOT_DEBUG_CHANNEL).send(f"[{type.upper()}]"+f" [{fromFunction.upper()}]"+f"  {content}")

def readback(what:str="all",deleteAfter:bool=False)->str:
    """

    gives back a str of all the file contents in the specified debug folder(s)
    <what>:
    all: errors, logs and loging errors
    error
    log
    log_error
    """

    if what not in ["all","error","log","log_error"]:
        return f"Bad argument: {what}"

    all_contents=""
    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))
    
    if what in ["all","error"]:
        all_contents+="------------\nErrors/crashes:\n"
        for file in sorted(Path(ROOT_PATH+"\\debug\\crash_reports").glob("*.txt")):
            all_contents+=f"{file.name}\n"+file.read_text(encoding="utf-8")+"\n\n"

    if what in ["all","log"]:
        all_contents+="------------\nLogs/Debug:\n"
        for file in sorted(Path(ROOT_PATH+"\\debug\\logs").glob("*.txt")):
            all_contents+=f"{file.name}\n"+file.read_text(encoding="utf-8")+"\n\n"

    if what in ["all","log"]:
        all_contents+="------------\nErrors during logging:\n"
        for file in sorted(Path(ROOT_PATH+"\\debug\\logs\\log_errors").glob("*.txt")):
            all_contents+=f"{file.name}\n"+file.read_text(encoding="utf-8")+"\n\n"
    
    if deleteAfter:
        clean(what)
    
    return all_contents

def clean(what:str="all"):
    """

    cleans out the specified folder in the debug folder\n
    <what>:\n
    all: errors, logs and loging errors\n
    error\n
    log\n
    log_error\n
    """
    ROOT_PATH=os.path.dirname(os.path.abspath(__file__))

    if what=="all":
        folder_path=Path(ROOT_PATH+"\\debug")
        if folder_path.exists():
            shutil.rmtree(folder_path)
        return
    
    if what=="error":
        folder_path=Path(ROOT_PATH+"\\debug\\crash_reports")
        if folder_path.exists():
            shutil.rmtree(folder_path)
    elif what=="log":
        folder_path=Path(ROOT_PATH+"\\debug\\logs")
        if folder_path.exists():
            shutil.rmtree(folder_path)
    elif what=="log_error":
        folder_path=Path(ROOT_PATH+"\\debug\\logs\\log_errors")
        if folder_path.exists():
            shutil.rmtree(folder_path)

setupFolders()
