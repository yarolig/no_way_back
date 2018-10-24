
import random
import pygame
import pygame.event
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
#        pygame.mixer.init()

        self.sounds = {}


        t = Track()
        t.file = 'Podington_Bear_-_11_-_Massive_Attack.ogg'
        t.ls_time = 59.55
        self.tracks.append(t)

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
        self.start_second_time = False

        self.current_track = t # random.choice(self.tracks)

    def init(self):
        pass

    def onStart(self):
        music_file = data.musicpath(self.current_track.file)
        logging.debug("music file: {}".format(music_file))
        self.music = pygame.mixer.music
        self.music.load(music_file)
        self.music.play(loops=0)
        self.music.set_endevent(pygame.USEREVENT)

        self.sounds['impact'] = pygame.mixer.Sound(data.musicpath('274943__theshaggyfreak__knock-knock1.ogg'))
        self.sounds['checkpoint'] = pygame.mixer.Sound(data.musicpath('332629__treasuresounds__item-pickup.ogg'))
        self.sounds['win'] = pygame.mixer.Sound(data.musicpath('147256__pjcohen__skiba22edge.ogg'))


    def onLevelStart(self, level):
        if self.start_second_time:
            self.change_music()
        else:
            self.start_second_time = True
            if self.current_track.ls_time:
                try:
                    self.music.set_pos(self.current_track.ls_time)
                except pygame.error:
                    pass

    def change_music(self):
        if self.music is None:
            return
        for i in xrange(10):
            t = random.choice(self.tracks)
            if t is not self.current_track:
                self.current_track = t
                break
        self.music.fadeout(300)
        music_file = data.musicpath(self.current_track.file)
        self.music.load(music_file)
        self.music.play(loops=-1)

    def onLevelEnd(self):
        pass


    def onExit(self):
        if self.music:
             self.music.fadeout(500)
             time.sleep(0.5)
             self.music = None
    def effect(self,name):
        self.sounds[name].play()