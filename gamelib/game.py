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
from . import worldgen
from . import race


def make_vector(x=0, y=0, z=0):
    v = np.ndarray(shape=(3,), dtype=float)
    v[0] = x
    v[1] = y
    v[2] = z
    return v


class Boat(object):
    model = 'boat'
    stationary = False
    vel_fade = 0.98
    def __init__(self):
        self.pos = make_vector(0, 0, 0)
        self.dir = make_vector(1, 1, 0)
        self.yaw = 0
        self.vel = make_vector(0, 0, 0)


    def draw(self, game):
        glPushMatrix(GL_MODELVIEW_MATRIX)
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        angle = math.atan2(self.dir[1], self.dir[0])
        glRotatef(180 + self.yaw * 180 / math.pi, 0, 0, 1)
        game.draw_model(self.model)
        glPopMatrix()


class Bouy(Boat):
    model = 'bouy'
    stationary = True


class Checkpoint(Boat):
    model = 'checkpoint'
    stationary = True

class Debris(Boat):
    model = 'checkpoint'
    ttl = 1000
    vel_fade = 0.1


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
    def __init__(self, app, racename='race1.png'):
        self.app = app
        p = Boat()
        p.pos = make_vector()
        p.dir = make_vector(0, 1, 0)
        self.player = p
        self.boats = []
        self.debris = []

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
        self.models['bouy'] = objloader.OBJ(filepath('bouy.obj'), swapyz=True)
        self.models['checkpoint'] = objloader.OBJ(filepath('checkpoint.obj'), swapyz=True)
        self.clock = pygame.time.Clock()
        self.ticks = 0

        self.actions = controls.make_actions()

        self.prepare_race(racename)
        self.prepare_water()

    def prepare_race(self, racename):
        self.race = race.Race()
        self.race.load(filepath(racename))
        sx, sy, sz = 20, 20, 1
        self.race.sx = sx
        self.race.sy = sy

        self.player.pos = make_vector(sx * self.race.startpos[0],
                                      sy * self.race.startpos[1])
        self.player.yaw = 270
        for x, y in self.race.bouys:
            b = Bouy()
            b.pos = make_vector(sx * x, sy * y, 0)
            self.boats.append(b)

        for x, y in self.race.checkpoints:
            b = Checkpoint()
            b.pos = make_vector(sx * x, sy * y, 1)
            self.boats.append(b)

        def color_for_e(e):
            if e <= -25:
                glColor3f(.4, .4, .5)
            elif e <= -15:
                glColor3f(.5, .5, .2)
            elif e <= 25:
                glColor3f(.6, .6, .1)
            elif e <= 505:
                glColor3f(.02, .5, .01)
            elif e <= 905:
                glColor3f(.5, .5, .5)
            else:
                glColor3f(.8, .9, .9)

        self.wlist = glGenLists(1)
        glNewList(self.wlist, GL_COMPILE)
        subx = 1
        suby = 1
        sx/=subx
        sy/=suby

        glBegin(GL_QUADS)
        for i in range(self.race.w*subx):
            logging.info('{}/{}'.format(i, self.race.w*subx))

            for j in range(self.race.h*suby):
                e1 = self.race.getfz((i + 0)/subx, (j + 0)/suby)
                e2 = self.race.getfz((i + 1)/subx, (j + 0)/suby)
                e3 = self.race.getfz((i + 1)/subx, (j + 1)/suby)
                e4 = self.race.getfz((i + 0)/subx, (j + 1)/suby)

                # print ('e1={}'.format(e1))
                color_for_e(e1)
                glVertex3f((i) * sx, (j) * sy, e1 * sz - 0.0)
                color_for_e(e2)
                glVertex3f((i + 1) * sx, (j) * sy, e2 * sz - 0.0)
                color_for_e(e3)
                glVertex3f((i + 1) * sx, (j + 1) * sy, e3 * sz - 0.0)
                color_for_e(e4)
                glVertex3f((i) * sx, (j + 1) * sy, e4 * sz - 0.0)
        glEnd()
        glEndList()

    def prepare_water(self):
        self.waterlist = glGenLists(1)
        glNewList(self.waterlist, GL_COMPILE)
        sx = 20.0*5
        sy = 20.0*5
        stx = 1.0
        sty = 1.0
        glColor4f(0.2, 0.4, 0.7, 0.5)
        glNormal3f(0.0,0.0,1.0)
        glBegin(GL_QUADS)
        for i in range(-30, self.race.w/5+30):
            for j in range(-30, self.race.h/5+30):
                glTexCoord2f((i) * stx, (j) * sty)
                glVertex3f((i) * sx, (j) * sy, 0.0)

                glTexCoord2f((i + 1) * stx, (j) * sty)
                glVertex3f((i + 1) * sx, (j) * sy, 0.0)

                glTexCoord2f((i + 1) * stx, (j) * sty)
                glVertex3f((i + 1) * sx, (j + 1) * sy, 0.0)
                glTexCoord2f((i) * stx, (j + 1) * sty)
                glVertex3f((i) * sx, (j + 1) * sy, 0.0)
        glEnd()
        glEndList()

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
        gluPerspective(90.0, w / h, 1.0, 10000.0)

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
    def setup_2d_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)

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

    def draw_water(self):
        #glEnable(GL_BLEND)
        #glBlendFunc(GL_CONSTANT_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA)
        #glDisable(GL_COLOR_MATERIAL)

        glCallList(self.waterlist)
        #glDisable(GL_BLEND)
        #glBlendFunc(GL_ONE, GL_ZERO)
        pass

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

        if True:
            glEnable(GL_DEPTH_TEST)

            glBegin(GL_LINES)
            glColor3f(1.0, 0.0, 0.0)

            for x, y, (fx, fy) in self.app.field.enum():
                x *= 30
                y *= 30
                # print([x,y,(fx, fy)])
                glVertex3f(x, y, 0)
                glVertex3f(x + fx * 30, y + fy * 30, 0)
            glEnd()

        self.debug_currents()

        glCallList(self.wlist)
        self.draw_water()
        self.no_lights()
        self.physics()
        self.ticks += 1
        if self.ticks % 100 == 0:
            pygame.display.set_caption("pyweek26: No Way Back FPS:{}".format(self.clock.get_fps()))


        self.setup_2d_camera()

    def debug_currents(self):
        boat = self.player
        xx = int(boat.pos[0]/self.race.sx)
        yy = int(boat.pos[1]/self.race.sy)

        glBegin(GL_LINES)
        glColor3f(0.0,1.0,0.0)
        n = 0

        glVertex3f(boat.pos[0], boat.pos[1], 0)
        glVertex3f(boat.pos[0], boat.pos[1], 10.0)

        for (x,y) in self.race.enum_currents(xx,yy):
            glColor3f(0.0,1.0,1.0)
            glVertex3f(boat.pos[0], boat.pos[1], 0)
            glVertex3f(boat.pos[0]-x*1000.0, boat.pos[1]-y*1000.0, 10.0)
            n+=1
            #if n > 20:
            #    break
        glEnd()



    def physics(self):
        if self.actions['a']:
            self.player.yaw += 0.1
        if self.actions['d']:
            self.player.yaw -= 0.1
        if self.actions['W']:
            self.player.vel += self.player.dir * 0.6
        if self.actions['w']:
            self.player.vel += self.player.dir * 0.06
        if self.actions['s']:
            self.player.vel -= self.player.dir * 0.06

        while len(self.debris) < 10:
            # add debris
            d = Debris()
            d.pos = self.player.pos + (random.randint(20, 40)*random.randint(-1,1),
                                       random.randint(20, 40)*random.randint(-1,1), 0)

            xx = int(d.pos[0]/self.race.sx)
            yy = int(d.pos[1]/self.race.sy)
            current = self.race.get_current(xx, yy)
            d.vel[0] = current[0]
            d.vel[1] = current[1]
            self.debris.append(d)

        self.debris = filter(lambda x:x.ttl>0, self.debris)

        self.phy_boat(self.player)
        for b in self.boats:
            self.phy_boat(b)

        for d in self.debris:
            self.phy_boat(d)



    def phy_boat(self, boat):
        if boat.stationary:
            return
        boat.pos += boat.vel
        xx = int(boat.pos[0]/self.race.sx)
        yy = int(boat.pos[1]/self.race.sy)
        current = self.race.get_current(xx, yy)
        #logging.info('current current {}'.format(current))
        boat.vel += current
        boat.vel *= boat.vel_fade
        boat.vel -= current


    def onKey(self, key):
        if key == pygame.K_a:
            self.player.yaw += 0.1
        elif key == pygame.K_d:
            self.player.yaw -= 0.1
        elif key == pygame.K_w:
            self.player.pos += self.player.dir * 100
        elif key == pygame.K_s:
            self.player.pos -= self.player.dir * 100
