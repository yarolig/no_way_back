import random
import pygame
import pygame.event
import logging
import time
from . import data


class Track(object):
    file = ''
    ls_time = 0.0
    volume_multiplier = 1.0


class Mus(object):
    def __init__(self, app):
        self.app = app
        self.music = None
        self.tracks = []
        self.sounds = {}
        self.sound_volume_multiplier = {}

        t = Track()
        t.file = 'Podington_Bear_-_11_-_Massive_Attack.ogg'
        t.ls_time = 59.55
        t.volume_multiplier = 0.1
        self.tracks.append(t)

        t = Track()
        t.file = 'Cutside_-_01_-_Secret_Of_3rd_Planet.ogg'
        t.volume_multiplier = 0.3
        self.tracks.append(t)

        t = Track()
        t.file = 'fascinating_earthbound_objects_-_03_-_pangs.ogg'
        t.volume_multiplier = 0.4
        self.tracks.append(t)

        t = Track()
        t.file = 'how_the_night_came_-_06_-_6_Pris.ogg'
        t.volume_multiplier = 1.0
        t.ls_time = 99.2
        self.tracks.append(t)

        self.start_second_time = False
        self.current_track = random.choice(self.tracks)

    def init(self):
        pass

    def create_music(self):
        self.music = pygame.mixer.music
        self.music.set_endevent(pygame.USEREVENT)

    def destroy_music(self):
        if self.music is None:
            return

    def onMusicVolumeChanged(self):
        if self.music:
            self.music.set_volume(self.current_track.volume_multiplier * float(self.app.config['MusicVolume']))

    def onMusicToggle(self):
        if self.app.config['Music'] == '1':
            self.create_music()
        else:
            if self.music:
                self.music.fadeout(100)
            self.music = None
        self.change_music()

    def onStart(self):
        if self.app.config['Music'] == '1':
            self.create_music()

            music_file = data.musicpath(self.current_track.file)
            logging.debug("music file: {}".format(music_file))
            self.music = pygame.mixer.music
            self.music.load(music_file)
            self.music.set_volume(self.current_track.volume_multiplier * float(self.app.config['MusicVolume']))
            self.music.play(loops=0)

        self.sounds['impact'] = pygame.mixer.Sound(
            data.musicpath('274943__theshaggyfreak__knock-knock1.ogg'))
        self.sound_volume_multiplier['impact'] = 1.0

        self.sounds['checkpoint'] = pygame.mixer.Sound(
            data.musicpath('332629__treasuresounds__item-pickup.ogg'))
        self.sound_volume_multiplier['checkpoint'] = 1.0

        self.sounds['win'] = pygame.mixer.Sound(
            data.musicpath('147256__pjcohen__skiba22edge.ogg'))
        self.sound_volume_multiplier['win'] = 0.4

    def onLevelStart(self, level):
        if self.music is None:
            return

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
        for i in range(10):
            t = random.choice(self.tracks)
            if t is not self.current_track:
                self.current_track = t
                break
        music_file = data.musicpath(self.current_track.file)
        self.music.load(music_file)
        self.music.set_volume(self.current_track.volume_multiplier * float(self.app.config['MusicVolume']))
        self.music.play(loops=0)

    def onLevelEnd(self):
        pass

    def onExit(self):
        if self.music:
            self.music.fadeout(500)
            self.music = None

    def effect(self, name):
        if self.app.config['Sound'] == '1':
            vm = self.sound_volume_multiplier[name]
            self.sounds[name].set_volume(vm * float(self.app.config['SoundVolume']))
            self.sounds[name].play()
