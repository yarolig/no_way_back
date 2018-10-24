



from . import data
import json
import os

def create_config(cfgpath):
    f = open(cfgpath, 'w')
    f.write("""
{
  "Music" : "1",
  "Resolution" : "800x600",
  "Fullscreen" : "0",
  "MusicVolume" : "1.0",
  "placeholder1" : "0",
  "placeholder2" : "0"
}
""")
    f.close()

def load_config():
    cfgpath = data.userpath('config.txt')
    if not os.path.exists(cfgpath):
        create_config(cfgpath)
    cfg = json.load(open(cfgpath))
    return cfg
