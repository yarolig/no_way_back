from . import data
import json
import os


def create_config(cfgpath):
    cfg = {
        "Music": "1",
        "MusicVolume": "1.0",
        "Sound" : "1",
        "SoundVolume" : "1.0",
        "Resolution": "800x600",
        "Fullscreen": "0",
        "NoCurrents": "0",
        "ShieldRegeneration": "1",
        "MoreTime": "1",
        "AllOpen" : "0",
        "placeholder1": "0",
        "placeholder2": "0"
    }
    save_config(cfg)


def load_config():
    cfgpath = data.userpath('config.txt')
    if not os.path.exists(cfgpath):
        create_config(cfgpath)
    cfg = json.load(open(cfgpath))
    return cfg


def save_config(cfg):
    s = json.dumps(cfg, indent=2)
    cfgpath = data.userpath('config.txt')
    f = open(cfgpath, 'w')
    f.write(s)
    f.close()
