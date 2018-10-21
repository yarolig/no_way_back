from __future__ import print_function
from . import data
from .gui import *

import logging
import pygame
import pygame.freetype
import time
from OpenGL import GL
from OpenGL import GLU

import pygame.examples
import numpy as np
import random
import math

class Boat(object):
    def __init__(self):
        self.pos = np.ndarray(shape=(2,), dtype=float)
        self.dir = np.ndarray(shape=(2,), dtype=float)
        self.vel = np.ndarray(shape=(2,), dtype=float)

class Sink(object):
    def __init__(self):
        self.flow = 0

class Field(object):
    def __init__(self):
        self.data = np.ndarray(shape=(100,100, 2), dtype=float)
        for i in range(100):
            for j in range(100):
                self.data[i][j][0] = 0.5
                self.data[i][j][1] = 0.5
    def enum(self):
        for i in range(32):
            for j in range(32):
                yield i,j,self.data[i][j]
    def change(self):
        for i in range(32):
            for j in range(32):
                self.data[i][j][0] += 0.001 * (random.randint(-100, 100) - random.randint(1, 10) * self.data[i][j][0])
                self.data[i][j][1] += 0.001 *(random.randint(-100, 100) - random.randint(1,10)*self.data[i][j][1])


class App(object):
    def __init__(self):
        self.boat = None
        self.debris = []
        self.field = Field()

        self.w = 800
        self.h = 600

    def get_screen_size(self):
        return (self.w, self.h)

    def select_menu(self, new_menu):
        self.active_menu = new_menu

    def start_game(self, difficulty='normal'):
        self.active_menu = None
        self.music.set_pos(59.55)


    def draw_game(self):
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        w, h = self.get_screen_size()
        GLU.gluOrtho2D(0, w, 0, h)
        GL.glBegin(GL.GL_LINES)
        GL.glColor3f(1.0, 1.0, 1.0)

        for x,y,(fx, fy) in self.field.enum():
            x*=30
            y*=30
            #print([x,y,(fx, fy)])
            GL.glVertex3f(x,y, 0)
            GL.glVertex3f(x+fx*30, y+fy*30, 0)
        GL.glEnd()

    def init(self):
        self.active_menu = None
        self.music = None

        logging.basicConfig(level=logging.DEBUG)

        logging.debug("mixer pre-init")
        pygame.mixer.pre_init()
        # logging.debug("pygame.init")
        # pygame.init()

        logging.debug("display.init")
        pygame.display.init()
        pygame.display.set_caption("pyweek26: No Way Back")

        logging.debug("set_mode")
        self.surface = pygame.display.set_mode(
            [self.w, self.h],
            pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
        )

        logging.debug("freetype")
        pygame.freetype.init()
        self.font = pygame.freetype.Font(None)

        logging.debug("mixer init")
        pygame.mixer.init(frequency=44100, buffer=1024*2)
        logging.debug("mixer init: {}".format(pygame.mixer.get_init()))

        self.new_menu = None
        self.save_menu = None
        self.load_menu = None
        self.main_menu = None
        self.options_menu = None
        self.sound_menu = None
        self.credits_menu = None

        def ss(d):
            return lambda: self.start_game(d)

        f = Frame()
        f.ypos += 100
        f.addButton("New Game", action=lambda: self.select_menu(self.new_menu))
        f.addButton("Load Game", action=lambda: self.select_menu(self.save_menu))
        f.addButton("Save Game", action=lambda: self.select_menu(self.load_menu))
        f.addButton("Options", action=lambda: self.select_menu(self.options_menu))
        f.addButton("Credits", action=lambda: self.select_menu(self.credits_menu))
        f.addButton("Exit", action=self.exit)
        self.main_menu = f

        f = Frame()
        f.ypos += 100
        f.addButton("Easy", action=ss('easy'))
        f.addButton("Normal", action=ss('normal'))
        f.addButton("Hard", action=ss('hard'))
        f.addButton("")
        f.addButton("Impossible", action=ss('impossible'))
        f.addButton("")
        f.addButton("Back", action=lambda: self.select_menu(self.main_menu))
        self.new_menu = f

        f = Frame()
        f.ypos += 100
        # f.addButton("Graphics",action=lambda:self.select_menu(self.sound_menu))
        f.addButton("Sound", action=lambda: self.select_menu(self.sound_menu))
        # f.addButton("Controls",action=lambda:self.select_menu(self.sound_menu))
        f.addButton("")
        f.addButton("Back", action=lambda: self.select_menu(self.main_menu))
        self.options_menu = f

        f = Frame()
        f.ypos += 100

        f.addButton("Play music")
        f.addButton("Music volume")
        f.addButton("")
        f.addButton("Sound volume")
        f.addButton("")
        f.addButton("Back", action=lambda: self.select_menu(self.options_menu))
        self.sound_menu = f

        #for i in range(3):
        #    self.draw()
        #    pygame.event.pump()

        self.select_menu(self.main_menu)

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
        else:
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
