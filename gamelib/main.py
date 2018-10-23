from __future__ import print_function
from . import data
from .gui import *
from .menu import *
from .game import *
from .controls import *

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
        self.field = Field()

        self.w = 800
        self.h = 600
        self.game = None

    def get_screen_size(self):
        return (self.w, self.h)

    def select_menu(self, new_menu):
        self.active_menu = new_menu

    def start_game(self, race):
        self.select_menu(self.loading_menu)
        pygame.event.pump()
        self.draw()
        pygame.event.pump()
        self.game = Game(self, race)
        self.music.set_pos(59.55)
        self.active_menu = None


    def draw_game(self):
        # GL.glMatrixMode(GL.GL_MODELVIEW)
        # GL.glLoadIdentity()
        # w, h = self.get_screen_size()
        # GLU.gluOrtho2D(0, w, 0, h)

        glEnable(GL_DEPTH_TEST)
        '''
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f(1.0, 1.0, 1.0)

        for x, y, (fx, fy) in self.field.enum():
            x *= 30
            y *= 30
            # print([x,y,(fx, fy)])
            GL.glVertex3f(x, y, 0)
            GL.glVertex3f(x + fx * 30, y + fy * 30, 0)
        GL.glEnd()
        '''

    def init(self):
        self.active_menu = None
        self.music = None

        logging.basicConfig(level=logging.DEBUG)

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
        self.font = pygame.freetype.Font(None)

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
            self.draw_game()

        pygame.display.flip()
        self.field.change()

    def start_music(self):
        music_file = data.musicpath("Podington_Bear_-_11_-_Massive_Attack.ogg")
        logging.debug("music file: {}".format(music_file))
        self.music = pygame.mixer.music
        self.music.load(music_file)
        self.music.play(loops=-1)

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
        if self.music:
            self.music.fadeout(500)
            time.sleep(0.5)
            self.music = None
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def mainloop(self):
        self.start_music()
        while True:
            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    if self.music:
                        self.music.fadeout(500)
                        time.sleep(0.5)
                    return
                if e.type == pygame.KEYUP:
                    if e.key == pygame.K_q:
                        self.exit()

                    if self.game:
                        if e.key == pygame.K_ESCAPE:
                            self.select_menu(self.new_menu)
                        else:
                            self.controls.onKey(e.key, False, self.game.actions)
                    # self.game.onKey(e.key)
                if e.type == pygame.KEYDOWN:
                    if self.game:
                        self.controls.onKey(e.key, True, self.game.actions)
                elif e.type == pygame.MOUSEMOTION:
                    if self.active_menu:
                        x, y = e.pos
                        self.active_menu.mouseMove(x, 600 - y)
                elif e.type == pygame.MOUSEBUTTONUP:
                    if self.active_menu:
                        self.active_menu.click()
                elif e.type == pygame.VIDEORESIZE:
                    self.onResize(e.w, e.h)
                else:
                    logging.debug("event {}".format(e))

            self.draw()
            time.sleep(0.001)


def main():
    app = App()
    app.init()
    app.mainloop()
    print("Hello from your game's main()")
    print(data.load('sample.txt').read())
