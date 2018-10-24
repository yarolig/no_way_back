import numpy as np
import random
import math
import logging
from . import glboilerplate

import pygame
import time

from OpenGL.GL import *
from OpenGL.GLU import *
import objloader
from .data import *
from . import controls
from . import race
from . import skybox


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
        # game.skybox.draw()
        glPopMatrix()


class Bouy(Boat):
    model = 'bouy'
    stationary = True


class Checkpoint(Boat):
    model = 'bouy'
    stationary = True


class Game(object):
    def __init__(self, app, racename='race1.png'):
        self.app = app
        p = Boat()
        p.pos = make_vector()
        p.dir = make_vector(0, 1, 0)
        self.player = p
        self.boats = []
        self.up = make_vector(0, 0, 1)
        self.models = {}
        self.models['boat'] = objloader.OBJ(modelpath('boat.obj'), swapyz=True)
        self.models['bouy'] = objloader.OBJ(filepath('checkpoint.obj'), swapyz=True)
        self.models['checkpoint'] = objloader.OBJ(filepath('bouy.obj'), swapyz=True)
        self.clock = pygame.time.Clock()
        self.ticks = 0

        self.actions = controls.make_actions()

        self.prepare_race(racename)
        self.prepare_water()
        self.prepare_deeps()
        self.skybox = skybox.Skybox()
        self.skybox.prepare()

    def prepare_race(self, racename):
        self.tertex = glboilerplate.Texture3D([

            filepath('dirt.png'),
            filepath('dirt.png'),
            filepath('sand.png'),
            filepath('sand.png'),
            filepath('grass.png'),
            filepath('grass.png'),
            filepath('hills.png'),
            filepath('hills.png'),
        ])
        self.race = race.Race()
        self.race.load(filepath(racename))
        sx, sy, sz = self.race.sx, self.race.sy, self.race.sz
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
                return (.4, .4, .5)
            elif e <= -15:
                return (.5, .5, .2)
            elif e <= 25:
                return (.6, .6, .1)
            elif e <= 505:
                return (.02, .5, .01)
            elif e <= 905:
                return (.5, .5, .5)
            else:
                return (.8, .9, .9)

        def w_for_e(e):
            e /= sz
            if e <= -25:
                return 0/4.0
            elif e <= -15:
                return 0/4.0
            elif e <= 25:
                return 1/4.0
            elif e <= 505:
                return 2/4.0
            elif e <= 905:
                return 3/4.0
            else:
                return 4/4.0

        subx = 1
        suby = 1
        sx /= subx
        sy /= suby

        floats = []

        def col(e):
            r, g, b = 1,1,1 #color_for_e(e)
            floats.append(r)
            floats.append(g)
            floats.append(b)

        def vert(x, y, z):
            floats.append(x)
            floats.append(y)
            floats.append(z)

            floats.append(x * 0.01)
            floats.append(y * 0.01)
            floats.append(w_for_e(z))


        for i in range(self.race.w * subx):
            logging.info('{}/{}'.format(i, self.race.w * subx))

            for j in range(self.race.h * suby):
                e1 = self.race.getfz((i + 0) / subx, (j + 0) / suby)
                e2 = self.race.getfz((i + 1) / subx, (j + 0) / suby)
                e3 = self.race.getfz((i + 1) / subx, (j + 1) / suby)
                e4 = self.race.getfz((i + 0) / subx, (j + 1) / suby)

                vert((i) * sx, (j) * sy, e1 * sz - 0.0)
                col(e1)

                vert((i + 1) * sx, (j) * sy, e2 * sz - 0.0)
                col(e2)

                vert((i + 1) * sx, (j + 1) * sy, e3 * sz - 0.0)
                col(e3)

                vert((i) * sx, (j + 1) * sy, e4 * sz - 0.0)
                col(e4)
        self.terrain = glboilerplate.VertexBuffer(
            floats,
            vertex_size=3,
            uv_size=3, uv_offset=3 * 4,
            color_size=3, color_offset=6 * 4,
            mode=GL_QUADS)
        self.terrain.prepare()

    def prepare_deeps(self):
        deeps_scale = 10.0
        deeps_overhang = 8
        deeps_depth = -30.0

        sx = self.race.sx * deeps_scale
        sy = self.race.sx * deeps_scale
        stx = 1.0
        sty = 1.0
        floats = []

        maxrw =deeps_scale*(int(self.race.w / deeps_scale) + 2)
        maxrh = deeps_scale*(int(self.race.h / deeps_scale) + 2)
        maxr = max(maxrw, maxrh)
        maxr = 1000.0
        def tex(a, b):
            floats.append(a)
            floats.append(b)

        def vert(x, y, z):
            floats.append(x)
            floats.append(y)
            r2 = (x*x + y*y)
            q = min(1000.0, (max(0, (maxr) ** 2 - r2))**0.5)
            #print('{} {} {} dd={} r2={}'.format(x,y,q,(maxr), r2**0.5))
            floats.append(-q - 0.5)

        ib = -deeps_overhang
        ie = int(self.race.w / deeps_scale) + deeps_overhang
        jb = -deeps_overhang
        je = int(self.race.h / deeps_scale) + deeps_overhang

        for i in range(ib, ie):
            for j in range(jb, je):
                dd = deeps_depth

                vert((i) * sx, (j) * sy, dd)
                tex((i) * stx, (j) * sty)

                vert((i + 1) * sx, (j) * sy, dd)
                tex((i + 1) * stx, (j) * sty)

                vert((i + 1) * sx, (j + 1) * sy, dd)
                tex((i + 1) * stx, (j) * sty)

                vert((i) * sx, (j + 1) * sy, dd)
                tex((i) * stx, (j + 1) * sty)
        self.deepsvb = glboilerplate.VertexBuffer(
            floats,
            uv_offset=8, uv_size=2,
            vertex_offset=0,
            mode=GL_QUADS
        )
        self.deepsvb.prepare()

    def prepare_water(self):
        water_scale = 5.0
        water_overhang = 15
        sx = self.race.sx * water_scale
        sy = self.race.sx * water_scale
        stx = 1.0
        sty = 1.0
        floats = []

        def tex(a, b):
            floats.append(a)
            floats.append(b)

        def vert(x, y, z):
            floats.append(x)
            floats.append(y)
            floats.append(z)

        for i in range(-water_overhang, int(self.race.w / water_scale) + water_overhang):
            for j in range(-water_overhang, int(self.race.h / water_scale) + water_overhang):
                vert((i) * sx, (j) * sy, 0.0)
                tex((i) * stx, (j) * sty)

                vert((i + 1) * sx, (j) * sy, 0.0)
                tex((i + 1) * stx, (j) * sty)

                vert((i + 1) * sx, (j + 1) * sy, 0.0)
                tex((i + 1) * stx, (j) * sty)

                vert((i) * sx, (j + 1) * sy, 0.0)
                tex((i) * stx, (j + 1) * sty)
        self.watervb = glboilerplate.VertexBuffer(
            floats,
            uv_offset=8, uv_size=2,
            vertex_offset=0,
            mode=GL_QUADS
        )
        self.watervb.prepare()

    def draw_model(self, name):
        model = self.models.get(name, None)
        if not model:
            logging.error("Model {} not loaded".format(name))
            return

        glCallList(self.models[name].gl_list)

    def setup_skybox_camera(self):
        self.setup_2d_camera()
        glMatrixMode(GL_MODELVIEW)
        #eye = - self.player.dir * 30.0 + self.up * 20.0
        #tgt = self.player.dir * 0.0
        eye = 3,4,5
        tgt = 1,1,1
        glLoadIdentity()
        gluLookAt(eye[0], eye[1], eye[2],
                  tgt[0], tgt[1], tgt[2],
                  self.up[0], self.up[1], self.up[2])


    def setup_3d_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w, h = list(map(float, list(self.app.get_screen_size())))
        gluPerspective(90.0, w / h, 1.0, 3000.0)

        self.player.dir = make_vector(math.cos(self.player.yaw),
                                      math.sin(self.player.yaw),
                                      0)
        glMatrixMode(GL_MODELVIEW)
        eye = self.player.pos - self.player.dir * 30.0 + self.up * 20.0
        tgt = self.player.pos + self.player.dir * 30.0 + self.up * 10.0
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

        glDisable(GL_BLEND)
        #glColor4f(.9, .0, .0, 1.0)
        glColor4f(.4, .4, .5, 1.0)
        glPushMatrix(GL_MODELVIEW_MATRIX)
        glTranslatef(self.player.pos[0], self.player.pos[1], self.player.pos[2])
        self.deepsvb.draw()

        glPopMatrix()

        glEnable(GL_BLEND)
        glColor4f(0.0, 0.07, 0.3, 0.5)
        glNormal3f(0.0, 0.0, 1.0)
        self.watervb.draw()
        glDisable(GL_BLEND)


    def draw(self):
        self.clock.tick()
        self.setup_skybox_camera()

        glColor4f(1,1,1,1)

        self.setup_3d_camera()

        glPushMatrix(GL_MODELVIEW_MATRIX)
        glTranslatef(self.player.pos[0], self.player.pos[1], self.player.pos[2])
        #angle = math.atan2(self.dir[1], self.dir[0])
        #glRotatef(180 + self.yaw * 180 / math.pi, 0, 0, 1)

        self.skybox.draw()
        glPopMatrix()


        self.setup_lights()
        self.player.draw(self)

        for b in self.boats:
            b.draw(self)


        self.tertex.bind()
        self.terrain.draw()
        self.tertex.unbind()

        self.draw_water()
        self.no_lights()
        self.physics()

        self.ticks += 1
        if self.ticks % 100 == 0:
            pygame.display.set_caption("pyweek26: No Way Back FPS:{}".format(self.clock.get_fps()))

        self.setup_2d_camera()

    def debug_currents(self):
        boat = self.player
        xx = int(boat.pos[0] / self.race.sx)
        yy = int(boat.pos[1] / self.race.sy)

        glBegin(GL_LINES)
        glColor3f(0.0, 1.0, 0.0)
        n = 0

        glVertex3f(boat.pos[0], boat.pos[1], 0)
        glVertex3f(boat.pos[0], boat.pos[1], 10.0)

        for (x, y) in self.race.enum_currents(xx, yy):
            glColor3f(0.0, 1.0, 1.0)
            glVertex3f(boat.pos[0], boat.pos[1], 0)
            glVertex3f(boat.pos[0] - x * 1000.0, boat.pos[1] - y * 1000.0, 10.0)
            n += 1
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

        self.phy_boat(self.player)
        for b in self.boats:
            self.phy_boat(b)

    def phy_boat(self, boat):
        if boat.stationary:
            return
        boat.pos += boat.vel
        xx = int(boat.pos[0] / self.race.sx)
        yy = int(boat.pos[1] / self.race.sy)
        current = self.race.get_current(xx, yy)
        # logging.info('current current {}'.format(current))
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
