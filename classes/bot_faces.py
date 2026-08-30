
from data_manage import load_json
from classes.file_paths import BotPaths

class Faces():
    faces=load_json(BotPaths.face_file)
    big_eyes="big_eyes"
    question="question"
    love="love"
    happy="happy"
    blush_happy="blush_happy"
    annoyed="annoyed"
    pat="pat"
    tired="tired"
    concentrate="concentrate"
    deep_concentrate="deep_concentrate"
    nervous="nervous"
    sleep="sleep"
    evil="evil"
    brain_hurt="brain_hurt"
    sad="sad"
    spark="spark"
    concerned="concerned"
    neutral="neutral"
    angry="angry"
    think="think"
    he="he?"
    excited="excited"

    class FaceBigCategory:
        happies=["love","blush_happy","pat","spark","excited"]
