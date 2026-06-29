
from data_manage import load_json

data=load_json("D:\\Python_Projects\\deadlock_bot_teszt\\map_graf.json")
for i,(key,value) in enumerate(data.items()):
    print(value)
    if key=="hint":
        continue
    for i in value["nexts"]:
        if i=="win":
            continue
        a=data[i]

"""    
    :{
        "nexts":["",""]
    },
"""