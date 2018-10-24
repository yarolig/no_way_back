
import random
import pygame
import logging
import time
from . import data

class Track(object):
    file = ''
    ls_time = 0.0



class Mus(object):
    def __init__(self, app):
        self.app = app
        self.music = None
        self.tracks = []

        t = Track()
        # t.file = 'Podington_Bear_-_11_-_Massive_Attack.ogg'
        # t.ls_time = 59.55
        # tracks.append(t)
        # self.current_track = t

        t = Track()
        t.file = 'Cutside_-_01_-_Secret_Of_3rd_Planet.ogg'
        self.tracks.append(t)

        t = Track()
        t.file = 'fascinating_earthbound_objects_-_03_-_pangs.ogg'
        self.tracks.append(t)

        t = Track()
        t.file = 'how_the_night_came_-_06_-_6_Pris.ogg'
        t.ls_time = 99.2
        self.tracks.append(t)
        self.current_track = t
        # self.current_track = random.choice(self.tracks)

    def init(self):
        pass

    def onStart(self):
        music_file = data.musicpath(self.current_track.file)
        logging.debug("music file: {}".format(music_file))
        self.music = pygame.mixer.music
        self.music.load(music_file)
        self.music.play(loops=-1)

    def onLevelStart(self, level):

        if self.current_track.ls_time:
            self.music.set_pos(self.current_track.ls_time)

    def onExit(self):
        if self.music:
             self.music.fadeout(500)
             time.sleep(0.5)
             self.music = None