from __future__ import print_function
from . import data
from .gui import *
from .menu import *
from .game import *
from .controls import *
from .config import *
from .mus import *

import logging
import pygame
import pygame.freetype
import time
from OpenGL import GL
from OpenGL import GLU

import numpy as np
import random
import math


class App(object):
    def __init__(self):
        self.boat = None
        self.debris = []

        self.w = 800
        self.h = 600
        self.game = None

    def get_screen_size(self):
        return (self.w, self.h)

    def select_menu(self, new_menu):
        self.active_menu = new_menu

    def start_custom_race(self, race, rt, laps=0):
        make_loading_menu(self)
        self.select_menu(self.loading_menu)
        pygame.event.pump()
        self.draw()
        pygame.event.pump()
        self.game = Game(self, race, rt, laps)
        self.active_menu = None
        self.mus.onLevelStart(race)

    def start_game(self, race):
        text = quests.intro_for_level(race)
        if text:
            make_loading_menu(self, text)
        else:
            make_loading_menu(self)

        self.select_menu(self.loading_menu)
        pygame.event.pump()
        self.draw()
        pygame.event.pump()
        self.game = Game(self, race)

        if not text:
            self.active_menu = None
            self.mus.onLevelStart(race)

    def is_race_completed(self, name):
        return self.config.get('completed_' + name, False)

    def set_race_completed(self, name):
        self.config['completed_' + name] = True
        self.save_config()

    def is_race_available(self, name):
        return self.config.get('available_' + name, False)

    def set_race_available(self, name):
        self.config['available_' + name] = True
        self.save_config()

    def set_race_mintime(self, name, t):
        oldt = int(self.config.get('mintime_' + name, 99999))
        self.config['mintime_' + name] = str(min(oldt, t))
        self.save_config()

    def set_race_maxtime(self, name, t):
        oldt = int(self.config.get('maxtime_' + name, 0))
        self.config['maxtime_' + name] = str(min(oldt, t))
        self.save_config()

    def set_race_record(self, name, t):
        oldt = float(self.config.get('record_' + name, 99999999))
        if oldt > t:
            self.config['record_' + name] = str(t)
            self.save_config()

    def get_race_record(self, name):
        t = self.config.get('record_' + name, 0)
        if not t:
            return ""
        fseconds = float(t)
        print (['fseconds=', fseconds])
        sf =  math.floor(math.fmod(fseconds, 1.0)*100.0)
        seconds = math.floor(math.fmod(fseconds, 60.0))
        minutes = math.floor(fseconds / 60.0)


        print (['sf=', sf])

        print (['seconds=', seconds])

        print (['minutes=', minutes])

        s = "{:02.0f}:{:02.0f}.{:02.0f}".format(minutes, seconds, sf)
        return s

    def continue_game(self):
        if not self.game:
            return
        self.active_menu = None

    def continue_game_accent(self):
        if not self.game:
            return
        self.mus.onLevelStart(race)
        self.active_menu = None

    def load_config(self):
        self.config = load_config()

    def save_config(self):
        save_config(self.config)

    def init(self):
        self.active_menu = None
        self.mus = Mus(self)

        self.load_config()

        self.w, self.h = list(map(int,
                                  self.config['Resolution'].split('x')))
        # logging.basicConfig(level=logging.DEBUG)

        logging.debug("mixer pre-init")
        pygame.mixer.pre_init()

        logging.debug("display.init")
        pygame.display.init()
        pygame.display.set_caption("pyweek26: No Way Back")

        logging.debug("set_mode")

        self.surface = pygame.display.set_mode(
            [self.w, self.h],
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE,
        )

        logging.debug("freetype")
        pygame.freetype.init()
        
        logging.debug("mixer init")
        pygame.mixer.init(frequency=44100, buffer=1024 * 2)
        logging.debug("mixer init: {}".format(pygame.mixer.get_init()))

        prepare_menu(self)
        self.select_menu(self.main_menu)
        self.controls = Controls()
        self.controls.load_config()

    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if self.active_menu:
            GL.glClearColor(0.5, 0.6, 0.7, 1.0)
        else:
            GL.glClearColor(0.3, 0.4, 0.9, 1.0)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        w, h = self.get_screen_size()
        GLU.gluOrtho2D(0, w, 0, h)
        if self.active_menu:
            self.active_menu.draw()
        elif self.game:
            self.game.draw()

        pygame.display.flip()

    def onResize(self, w, h):
        # TODO: delay resize
        self.w = w
        self.h = h
        logging.debug("set_mode")
        self.surface = pygame.display.set_mode(
            [self.w, self.h],
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )
        GL.glViewport(0, 0, w, h)
        logging.debug("on resize {} {}".format(w, h))
        logging.debug("info: {}".format(pygame.display.Info()))

    def exit(self):
        self.mus.onExit()
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def mainloop(self):
        self.mus.onStart()
        while True:
            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    self.mus.onExit()
                    return
                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_F10:
                        self.exit()
                    if self.game:
                        if e.key == pygame.K_ESCAPE:
                            self.select_menu(self.main_menu)
                        else:
                            self.controls.onKey(e.key, False, self.game.actions)
                if e.type == pygame.KEYDOWN:
                    if self.game:
                        self.controls.onKey(e.key, True, self.game.actions)
                elif e.type == pygame.MOUSEMOTION:
                    if self.active_menu:
                        x, y = e.pos
                        self.active_menu.mouseMove(x, self.h - y)
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.active_menu:
                        self.active_menu.click()
                elif e.type == pygame.VIDEORESIZE:
                    self.onResize(e.w, e.h)
                elif e.type == pygame.USEREVENT:
                    self.mus.change_music()
                else:
                    logging.debug("event {}".format(e))

            self.draw()
            time.sleep(0.001)


def main():
    app = App()
    app.init()
    app.mainloop()
