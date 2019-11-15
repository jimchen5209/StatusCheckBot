import psutil
import os
import json
from pathlib import Path

path = str(Path.home()) + '/.bot_status'

if not os.path.isdir(path):
    os.mkdir(path)

def getStatus():
    status = {}

    for walk in os.walk(path):
        for file in walk[2]:
            f = open(path + '/' + file, 'r')
            bot_status = json.loads(f.read())
            try:
                p = psutil.Process(bot_status['pid'])
                if p.cmdline()[1] == bot_status['cmdline'][0] and p.name().startswith('python'):        
                    status[bot_status['name']] = {'online': True}
            except psutil.NoSuchProcess:
                status[bot_status['name']] = {'online': False}
            f.close()
    return status

print(getStatus())