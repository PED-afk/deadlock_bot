
import os


def getTemp():
    return "CPU tempriture: "+str(os.popen('vcgencmd measure_temp').readline())

def usedSpace():
    return "Used storage space: "+str(os.popen("df -h /").read())+"%"

def ramUse():
    return "RAM in use: "+str(os.popen('free').read())

def uptime():
    a=str(os.popen('uptime').readline())
    return "CPU uptime: "+a

def getAll():
    data=[getTemp(),usedSpace(),ramUse(),uptime()]
    return "\n".join(data)


