
import random


def chooseFaceFromCategory(bot,category:str):
    if category in bot.faces:
        faces=bot.faces[category]
    else:
        faces=["(face category not found)"]
    r=random.randint(0,len(faces)-1)
    return faces[r]