import numpy as np
import random
import math
import logging

import pygame
import time

from OpenGL.GL import *
from OpenGL.GLU import *
import objloader
from .data import *
from . import controls


def make_vector(x=0, y=0, z=0):
    v = np.ndarray(shape=(3,), dtype=float)
    v[0] = x
    v[1] = y
    v[2] = z
    return v


class Boat(object):
    def __init__(self):
        self.pos = make_vector(0, 0, 0)
        self.dir = make_vector(1, 1, 0)
        self.yaw = 0
        self.vel = make_vector(0, 0, 0)
        self.model = 'boat'

    def draw(self, game):
        glPushMatrix(GL_MODELVIEW_MATRIX)

        glTranslatef(self.pos[0], self.pos[1], self.pos[2])

        angle = 0
        angle = math.atan2(self.dir[1], self.dir[0])
        # angle = pygame.time.get_ticks()* 0.001
        glRotatef(180 + self.yaw * 180 / math.pi, 0, 0, 1)

        logging.info("angle {}".format(angle))

        game.draw_model(self.model)
        glPopMatrix()


class Sink(object):
    def __init__(self):
        self.flow = 0


class Field(object):
    def __init__(self):
        self.data = np.ndarray(shape=(100, 100, 2), dtype=float)
        for i in range(100):
            for j in range(100):
                self.data[i][j][0] = 0.5
                self.data[i][j][1] = 0.5

    def enum(self):
        for i in range(32):
            for j in range(32):
                yield i, j, self.data[i][j]

    def change(self):
        for i in range(32):
            for j in range(32):
                self.data[i][j][0] += 0.001 * (random.randint(-100, 100) - random.randint(1, 10) * self.data[i][j][0])
                self.data[i][j][1] += 0.001 * (random.randint(-100, 100) - random.randint(1, 10) * self.data[i][j][1])


class Game(object):
    def __init__(self, app):
        self.app = app
        p = Boat()
        p.pos = make_vector()
        p.dir = make_vector(0, 1, 0)
        self.player = p
        self.boats = []

        b = Boat()
        b.pos = make_vector(0, 100, 0)
        b.yaw = 0
        b.dir = make_vector(1, 0, 0)
        self.boats.append(b)

        b = Boat()
        b.pos = make_vector(100, 100, 0)
        b.yaw = 90
        b.dir = make_vector(1, 1, 0)
        self.boats.append(b)

        self.up = make_vector(0, 0, 1)
        self.models = {}
        self.models['boat'] = objloader.OBJ(modelpath('boat.obj'), swapyz=True)
        self.clock = pygame.time.Clock()

        self.actions = controls.make_actions()

    def draw_model(self, name):
        model = self.models.get(name, None)
        if not model:
            logging.error("Model {} not loaded".format(name))
            return
        glCallList(self.models[name].gl_list)

    def setup_3d_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w, h = map(float, list(self.app.get_screen_size()))
        gluPerspective(90.0, w / h, 1.0, 1000.0)

        self.player.dir = make_vector(math.cos(self.player.yaw),
                                      math.sin(self.player.yaw),
                                      0)
        glMatrixMode(GL_MODELVIEW)
        eye = self.player.pos - self.player.dir * 30.0 + self.up * 20.0
        tgt = self.player.pos + self.player.dir * 0.0
        glLoadIdentity()
        gluLookAt(eye[0], eye[1], eye[2],
                  tgt[0], tgt[1], tgt[2],
                  self.up[0], self.up[1], self.up[2])
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)

    def setup_lights(self):
        glEnable(GL_LIGHTING)

        # sun
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0, 100, 100, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.5])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5])

        # sky
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [0, 0, 100])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.3, 0.9])
        glLightfv(GL_LIGHT2, GL_AMBIENT, [0.0, 0.0, 0.0])

        # ground
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [0, 0, -100])
        glLightfv(GL_LIGHT2, GL_DIFFUSE, [0.1, 0.1, 0.1])
        glLightfv(GL_LIGHT2, GL_AMBIENT, [0.0, 0.0, 0.0])

        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)

    def no_lights(self):

        glDisable(GL_LIGHTING)

    def draw(self):
        self.clock.tick()
        self.setup_3d_camera()

        if 1:
            self.setup_lights()
        else:

            glLightfv(GL_LIGHT0, GL_POSITION, (-40, 200, 100, 0.0))
            glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
            glEnable(GL_LIGHT0)
            glEnable(GL_LIGHTING)
            glEnable(GL_COLOR_MATERIAL)
            glEnable(GL_DEPTH_TEST)
            glShadeModel(GL_SMOOTH)

        self.player.draw(self)
        for b in self.boats:
            b.draw(self)
        self.no_lights()
        self.physics()

    def physics(self):
        if self.actions['a']:
            self.player.yaw += 0.1
        if self.actions['d']:
            self.player.yaw -= 0.1
        if self.actions['w']:
            self.player.vel += self.player.dir * 0.06
        if self.actions['s']:
            self.player.vel -= self.player.dir * 0.06

        self.phy_boat(self.player)
        for b in self.boats:
            self.phy_boat(b)

    def phy_boat(self, boat):
        boat.pos += boat.vel
        boat.vel *= 0.98

    def onKey(self, key):
        if key == pygame.K_a:
            self.player.yaw += 0.1
        elif key == pygame.K_d:
            self.player.yaw -= 0.1
        elif key == pygame.K_w:
            self.player.pos += self.player.dir * 10
        elif key == pygame.K_s:
            self.player.pos -= self.player.dir * 10
