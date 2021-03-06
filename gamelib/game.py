import numpy as np
import random
import math
import logging
from . import glboilerplate

import pygame
import time
import json

from OpenGL.GL import *
from OpenGL.GLU import *

import objloader
import pywavefront
import pywavefront.visualization

from .data import *
from . import controls
from . import race
from . import skybox
from . import gui


def make_vector(x=0, y=0, z=0):
    v = np.ndarray(shape=(3,), dtype=float)
    v[0] = x
    v[1] = y
    v[2] = z
    return v


def vector_len(v):
    x, y, z = v
    r = (x * x + y * y + z * z) ** 0.5
    return r


def normalized_vector(v):
    l = vector_len(v)
    if math.fabs(l) < 0.001:
        return v
    return v * (1.0 / l)


def dot_product(va, vb):
    return va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]


def bind_texture_hack(texture):
    if not getattr(texture, 'image', None):
        texture.image = gettexture2d(texture.path)
        texture.image.target = GL_TEXTURE_2D
        texture.image.id = texture.image.id
    texture.image.bind()


pywavefront.visualization.bind_texture = bind_texture_hack


all_3d_textures = {}
def gettexture3d(filenames):
    joined = '@@@'.join(filenames)
    cached = all_3d_textures.get(joined)
    if cached:
        return cached
    t = glboilerplate.Texture3D(filenames)
    all_3d_textures[joined] = t
    return t

all_2d_textures = {}
def gettexture2d(filename):
    cached = all_2d_textures.get(filename)
    if cached:
        return cached
    t = glboilerplate.Texture(filename)
    all_2d_textures[filename] = t
    return t


all_models = {}
def getmodel(filename):
    cached = all_models.get(filename)
    if cached:
        return cached
    t = pywavefront.Wavefront(filename)
    all_models[filename] = t
    return t



class Boat(object):
    model = 'boat'
    stationary = False
    vel_fade = 0.98
    hp = 10
    shield_ttl = 50
    maxhp = 10
    destroy_on_impact = False
    ignore_terrain = False
    destroyed = False
    quiet = False

    def __init__(self):
        self.pos = make_vector(0, 0, 0)
        self.dir = make_vector(1, 1, 0)
        self.yaw = 0
        self.rudder = 0
        self.dyaw = 0

        self.roll = 0
        self.droll = 0
        self.pitch = 0
        self.dpitch = 0

        self.vel = make_vector(0, 0, 0)

    def draw(self, game):
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        angle = math.atan2(self.dir[1], self.dir[0])
        glRotatef(180 + self.yaw * 180 / math.pi, 0, 0, 1)
        game.draw_model(self.model)
        # game.skybox.draw()
        glPopMatrix()


class Bouy(Boat):
    model = 'bouy'
    stationary = True


class Ship(Boat):
    model = 'ship'
    stationary = True


class Checkpoint(Boat):
    model = 'checkpoint'
    stationary = True
    visited = False


class Endpoint(Boat):
    model = 'endpoint'
    stationary = True
    visited = False


class Debris(Boat):
    model = 'bouy'
    stationary = False
    vel_fade = 0.1
    ttl = 500
    destroy_on_impact = True
    ignore_terrain = True
    quiet = True
    path = None

    def draw(self, game):
        if self.path is None:
            self.path = []
        v = make_vector()
        v += self.pos
        self.path.append(v)

        if self.ttl < 100:
            glColor4f(0.01 * self.ttl,
                      0.01 * self.ttl,
                      0.01 * self.ttl,
                      0.01 * self.ttl)
        else:
            glColor4f(1, 1, 1, 0.5)

        pl = len(self.path)
        p0 = 0
        p1 = int(0.1 * pl)
        p2 = int(0.3 * pl)
        p3 = int(0.5 * pl)
        p4 = int(0.9 * pl)
        glVertex3f(self.pos[0], self.pos[1], self.pos[2])
        glVertex3f(self.path[p4][0], self.path[p4][1], self.path[p4][2])

        glVertex3f(self.path[p4][0], self.path[p4][1], self.path[p4][2])
        glVertex3f(self.path[p3][0], self.path[p3][1], self.path[p3][2])

        glVertex3f(self.path[p3][0], self.path[p3][1], self.path[p3][2])
        glVertex3f(self.path[p2][0], self.path[p2][1], self.path[p2][2])

        glVertex3f(self.path[p2][0], self.path[p2][1], self.path[p2][2])
        glVertex3f(self.path[p1][0], self.path[p1][1], self.path[p1][2])

        glVertex3f(self.path[p1][0], self.path[p1][1], self.path[p1][2])
        glVertex3f(self.path[p0][0], self.path[p0][1], self.path[p0][2])


class Game(object):
    def init_gui(self):
        self.frame = gui.Frame(self.app)
        self.counter = self.frame.add_button("99")
        self.counter.x = self.app.get_screen_size()[0] / 2 - 10

        self.frame.pxsize = 32
        self.frame.ypos = 32
        self.hpbar = self.frame.add_volumebox()
        self.counter.color = pygame.Color('yellow')
        self.hpbar.color = pygame.Color(40, 100, 130)

    def update_hpbar(self):
        self.hpbar.color = pygame.Color(40, 100, 130)
        if self.player.shield_ttl > 0:
            self.hpbar.color = pygame.Color(150, 210, 250)

        self.hpbar.value = max(0, self.player.hp)
        self.hpbar.maxvalue = self.player.maxhp

    def update_counter(self):
        if self.winned:
            self.counter.text = "Win!"
        elif self.losed:
            self.counter.color = pygame.Color(230, 120, 120)
            self.counter.text = "Fail!"
        else:
            if self.timer_inc:
                self.counter.text = "{}".format(self.time_left)
                if self.laps > 1:
                    self.counter.text += (" {}/{}".format(self.current_lap, self.laps))
            else:
                self.counter.text = "--"

    def __init__(self, app, racename='race1.png', race_type=None, laps=0):
        self.app = app
        self.racename = racename
        self.init_gui()
        self.mouse_motion = [0.0, 0.0]
        self.cam_yaw = 0.0
        self.cam_pitch = 0.0
        p = Boat()
        p.pos = make_vector()
        p.dir = make_vector(0, 1, 0)

        if self.app.config['ShieldRegeneration'] == '1':
            p.maxhp = 20
            p.hp = 20
        self.player = p
        self.boats = []
        self.checkpoints = []
        self.endpoints = []
        self.debris = []
        self.winned = False
        self.losed = False
        self.current_lap = 0
        self.laps = laps
        self.up = make_vector(0, 0, 1)
        self.models = {}
        self.time_left = 0
        self.timer_inc = 0
        self.win_timeout = 0

        self.models['boat'] = getmodel(filepath('motorboat.obj'))
        self.models['ship'] = getmodel(modelpath('boat.obj'))
        self.models['bouy'] = getmodel(filepath('checkpoint.obj'))
        self.models['checkpoint'] = getmodel(filepath('buoy.obj'))
        self.models['endpoint'] = getmodel(filepath('endpoint.obj'))

        self.clock = pygame.time.Clock()
        self.ticks = 0

        self.actions = controls.make_actions()

        self.prepare_race(racename)
        if race_type:
            self.race_type = race_type
        if not self.laps:
            self.laps = int(self.race.config.get('laps', 1))
        self.init_race_logic()
        self.prepare_water()
        self.prepare_deeps()
        self.skybox = skybox.Skybox()
        self.skybox.prepare()

    def prepare_race(self, racename):
        self.tertex = gettexture3d([
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
        self.race_type = self.race.config['type']

        for x, y in self.race.bouys:
            b = Bouy()
            b.pos = make_vector(sx * x, sy * y, 0)
            self.boats.append(b)

        for x, y in self.race.ships:
            b = Ship()
            b.pos = make_vector(sx * x, sy * y, 0)
            self.boats.append(b)

        for x, y in self.race.boats:
            b = Boat()
            b.pos = make_vector(sx * x, sy * y, 0)
            b.destroy_on_impact = True
            self.boats.append(b)

        #print(['checkpoint count = ', len(self.race.checkpoints)])
        for x, y in self.race.checkpoints:
            b = Checkpoint()
            b.pos = make_vector(sx * x, sy * y, 1)
            self.boats.append(b)
            self.checkpoints.append(b)

        for x, y in self.race.endpoints:
            b = Endpoint()
            b.pos = make_vector(sx * x, sy * y, 1)
            self.boats.append(b)
            self.endpoints.append(b)

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
                return 0 / 4.0
            elif e <= -15:
                return 0 / 4.0
            elif e <= 25:
                return 1 / 4.0
            elif e <= 505:
                return 2 / 4.0
            elif e <= 905:
                return 3 / 4.0
            else:
                return 4 / 4.0

        subx = 1
        suby = 1
        sx /= subx
        sy /= suby

        floats = []

        def col(e):
            r, g, b = 1, 1, 1  # color_for_e(e)
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

        maxrw = deeps_scale * (int(self.race.w / deeps_scale) + 2)
        maxrh = deeps_scale * (int(self.race.h / deeps_scale) + 2)
        maxr = max(maxrw, maxrh)
        maxr = 1000.0

        def tex(a, b):
            floats.append(a)
            floats.append(b)

        def vert(x, y, z):
            floats.append(x)
            floats.append(y)
            r2 = (x * x + y * y)
            q = min(1000.0, (max(0, (maxr) ** 2 - r2)) ** 0.5)
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
        self.water_tex = gettexture2d(filepath('water.png'))
        water_scale = 5.0
        water_overhang = 15
        sx = self.race.sx * water_scale
        sy = self.race.sx * water_scale
        stx = 10.0
        sty = 10.0
        floats = []

        def tex(a, b):
            floats.append(a)
            floats.append(b)

        def vert(x, y, z):
            floats.append(x)
            floats.append(y)
            floats.append(z)

        for i in range(-water_overhang, int(self.race.w / water_scale) + water_overhang):
            for j in range(-water_overhang,
                           int(self.race.h / water_scale) + water_overhang):
                vert((i) * sx, (j) * sy, 0.0)
                tex((i) * stx, (j) * sty)

                vert((i + 1) * sx, (j) * sy, 0.0)
                tex((i + 1) * stx, (j) * sty)

                vert((i + 1) * sx, (j + 1) * sy, 0.0)
                tex((i + 1) * stx, (j + 1) * sty)

                vert((i) * sx, (j + 1) * sy, 0.0)
                tex((i) * stx, (j + 1) * sty)
        self.watervb = glboilerplate.VertexBuffer(
            floats,
            uv_offset=3 * 4, uv_size=2,
            vertex_offset=0,
            mode=GL_QUADS
        )
        self.watervb.prepare()

    def draw_model(self, name):
        model = self.models.get(name, None)
        if not model:
            logging.error("Model {} not loaded".format(name))
            return

        # glCallList(self.models[name].gl_list)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslate(0, 0, 0)
        glRotate(90, 1, 0, 0)
        pywavefront.visualization.draw(self.models[name])
        glPopMatrix()

    def setup_skybox_camera(self):
        self.setup_2d_camera()
        glMatrixMode(GL_MODELVIEW)
        # eye = - self.player.dir * 30.0 + self.up * 20.0
        # tgt = self.player.dir * 0.0
        eye = 3, 4, 5
        tgt = 1, 1, 1
        glLoadIdentity()
        gluLookAt(eye[0], eye[1], eye[2],
                  tgt[0], tgt[1], tgt[2],
                  self.up[0], self.up[1], self.up[2])

    def setup_3d_camera(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        w, h = list(map(float, list(self.app.get_screen_size())))
        gluPerspective(90.0, w / h, 1.0, 3000.0 * 10)

        self.player.dir = make_vector(math.cos(self.player.yaw),
                                      math.sin(self.player.yaw),
                                      0)
        if self.actions['mouse']:
            self.cam_yaw += self.mouse_motion[0] * 0.01
            self.mouse_motion[0] = 0
        else:
            self.cam_yaw *= 0.8

        cdir = make_vector(math.cos(self.player.yaw + self.cam_yaw),
                           math.sin(self.player.yaw + self.cam_yaw),
                           0)
        glMatrixMode(GL_MODELVIEW)

        eye = self.player.pos - cdir * 30.0 + self.up * 20.0
        tgt = self.player.pos + cdir * 30.0 + self.up * 10.0
        if self.actions['b']:
            tgt = self.player.pos - self.player.dir * 30.0 + self.up * 10.0
            eye = self.player.pos + self.player.dir * 30.0 + self.up * 20.0

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
        w, h = self.app.get_screen_size()
        gluOrtho2D(0, w, 0, h)

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
        # glColor4f(.9, .0, .0, 1.0)
        glColor4f(.4, .4, .5, 1.0)
        glPushMatrix()
        glTranslatef(self.player.pos[0], self.player.pos[1], self.player.pos[2])
        self.deepsvb.draw()

        glPopMatrix()

        glEnable(GL_BLEND)
        # glDisable(GL_BLEND)
        glColor4f(1.0, 1.0, 1.0, 0.5)
        glNormal3f(0.0, 0.0, 1.0)
        self.water_tex.bind()
        self.watervb.draw()
        self.water_tex.unbind()
        glDisable(GL_BLEND)

    def draw(self):
        self.setup_skybox_camera()

        glColor4f(1, 1, 1, 1)

        self.setup_3d_camera()

        glPushMatrix()
        glTranslatef(self.player.pos[0], self.player.pos[1], self.player.pos[2])
        # angle = math.atan2(self.dir[1], self.dir[0])
        # glRotatef(180 + self.yaw * 180 / math.pi, 0, 0, 1)

        self.skybox.draw()
        glPopMatrix()
        self.setup_lights()

        glEnable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 0.5)
        glBegin(GL_LINES)
        for b in self.debris:
            b.draw(self)
        glEnd()
        glColor4f(1.0, 1.0, 1.0, 1.0)

        self.player.draw(self)

        for b in self.boats:
            if vector_len(b.pos - self.player.pos) < 1000.0:
                b.draw(self)

        glEnable(GL_CULL_FACE)
        self.tertex.bind()
        self.terrain.draw()
        self.tertex.unbind()
        glDisable(GL_CULL_FACE)

        self.draw_water()
        self.no_lights()
        self.physics()
        self.logic()
        self.add_debris()

        self.ticks += 1
        if self.ticks % 100 == 0:
            pygame.display.set_caption(
                "pyweek26: No Way Back FPS:{}".format(self.clock.get_fps()))

        self.setup_2d_camera()
        self.frame.draw()

        if True:
            self.clock.tick(60)
        else:
            self.clock.tick_busy_loop(60)

    def start_with_more_time(self):
        if self.app.config['MoreTime'] == '1':
            self.time_left += 20

    def cp_more_time(self, cp_time):
        if self.app.config['MoreTime'] == '1':
            self.time_left += min(cp_time, 10)

    def init_race_logic(self):
        if self.race_type == 'checkpoints':
            self.time_left = int(self.race.config['start_time'])
            self.timer_inc = -1  ###
            self.start_with_more_time()
        elif self.race_type == 'countdown':
            self.time_left = int(self.race.config['start_time'])
            self.timer_inc = -1
            self.start_with_more_time()
        elif self.race_type == 'countup':
            self.time_left = 0
            self.timer_inc = 1
        elif self.race_type == 'circuit':
            self.time_left = int(self.race.config['start_time'])
            self.timer_inc = -1
            self.start_with_more_time()

    def checkpoint_hitted(self):
        if self.race_type == 'checkpoints':
            if not self.timer_inc:
                self.timer_inc = -1
                self.time_left = int(self.race.config['start_time'])
            self.time_left += int(self.race.config['cp_time'])
            if self.app.config['MoreTime'] == '1':
                # again
                self.cp_more_time(int(self.race.config['cp_time']))
        elif self.race_type == 'countdown':
            pass
        elif self.race_type == 'countup':
            pass
        elif self.race_type == 'circuit':
            if not self.timer_inc:
                self.timer_inc = -1
                self.time_left = int(self.race.config['start_time'])
            self.time_left += int(self.race.config['cp_time'])
            if self.app.config['MoreTime'] == '1':
                # again
                self.cp_more_time(int(self.race.config['cp_time']))

    def race_logic(self):
        if self.race_type == 'checkpoints':
            if self.timer_inc:
                if self.time_left < 0:
                    self.losed = True
                    self.timer_inc = 0
        elif self.race_type == 'countdown':
            if self.timer_inc:
                if self.time_left < 0:
                    self.losed = True
                    self.timer_inc = 0
        elif self.race_type == 'countup':
            pass
        elif self.race_type == 'circuit':
            if self.timer_inc:
                if self.time_left < 0:
                    self.losed = True
                    self.timer_inc = 0

    def logic(self):
        self.update_hpbar()
        self.update_counter()
        if self.ticks % 50 == 0:
            self.race_logic()
            self.time_left += self.timer_inc

        if self.player.hp <= 0:
            self.losed = True
        if self.win_timeout == 1:
            self.app.select_menu(self.app.new_menu)
            self.win_timeout = 0
            return
        if self.win_timeout > 0:
            self.win_timeout -= 1
        if self.winned or self.losed:
            return

        win = True
        hit = False
        if not self.checkpoints and not self.endpoints:
            return

        for cp in self.checkpoints:
            if cp.visited:
                continue
            win = False
            d = cp.pos - self.player.pos
            if vector_len(d) < 30:
                cp.visited = True
                cp.pos[2] -= 10.0
                hit = True

        if not self.endpoints:
            pass
        else:
            for cp in self.endpoints:
                d = cp.pos - self.player.pos
                if vector_len(d) < 30:
                    break
            else:
                win = False
        if win and self.laps > 1:
            self.current_lap += 1
            if self.current_lap < self.laps:
                win = False
                self.app.mus.effect('checkpoint')
                for cp in self.checkpoints:
                    cp.visited = False
                    cp.pos[2] += 10.0
        if win:
            self.on_win()
            self.app.mus.effect('win')
            self.app.mus.onLevelEnd()
            self.win_timeout = 100
            for cp in self.checkpoints:
                cp.visited = False
        elif hit:
            self.checkpoint_hitted()
            self.app.mus.effect('checkpoint')

    def on_win(self):
        self.winned = True
        self.app.set_race_record(self.racename, self.ticks / 50.0)
        self.app.set_race_completed(self.racename)
        for racename in self.race.config['next_races'].split():
            self.app.set_race_available(racename)

        self.app.new_menu.update(self.app, self.app.new_menu)

    def add_debris(self):
        self.debris = [x for x in self.debris if x.ttl > 0]
        for d in self.debris:
            d.ttl -= 1

        if self.ticks % 50 == 0:
            for i in range(6):
                for anomaly in self.race.anomalies:
                    (x, y, z) = anomaly.pos_for_debris(self.race.sx)
                    pos = make_vector(x, y, 0)
                    if vector_len(pos - self.player.pos) > 1000.0:
                        continue
                    d = Debris()
                    d.pos = pos
                    d.pos[2] += -0.1 * random.randint(1, 100)
                    d.ttl = 150
                    self.debris.append(d)
                    if len(self.debris) > 50:
                        return

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
        self.player.rudder = 0.0
        if self.actions['a']:
            self.player.rudder += 0.1
        if self.actions['d']:
            self.player.rudder += -0.1
        if self.actions['W']:
            self.player.vel += self.player.dir * 0.6
        if self.actions['w']:
            self.player.vel += self.player.dir * 0.06
        if self.actions['s']:
            self.player.vel -= self.player.dir * 0.06

        self.phy_boat(self.player)
        for b in self.boats:
            self.phy_boat(b)
        for b in self.debris:
            self.phy_boat(b)

    def phy_boat(self, boat):
        if boat.stationary or boat.destroyed:
            return

        if boat.shield_ttl > 0:
            boat.shield_ttl -= 1

        if self.app.config['ShieldRegeneration'] == '1':
            if boat.hp < boat.maxhp:
                if self.ticks % 1000 == 0:
                    boat.hp += 1

        for i in range(1, 3):
            if boat.ignore_terrain:
                continue
            l = 1.0 / max(1.0, vector_len(boat.vel))
            direction = boat.vel * l

            newpos = boat.pos + direction * i * 4.0
            newz = self.race.getfz2((newpos[0] + 0.5 * self.race.sx) / self.race.sx,
                                    (newpos[1] + 0.5 * self.race.sy) / self.race.sy)
            if newz > 0.0:
                boat.vel = -0.9 / i * boat.vel

                if boat.shield_ttl == 0:
                    boat.hp -= 1
                    boat.shield_ttl = 100
                    if not boat.quiet:
                        self.app.mus.effect('impact')
                if boat.destroy_on_impact:
                    boat.destroyed = True
                    boat.pos[2] -= 5.0
        else:
            boat.pos += boat.vel

        xx = int(boat.pos[0] / self.race.sx)
        yy = int(boat.pos[1] / self.race.sy)
        current = self.race.get_current(xx, yy)
        # if boat is self.player:
        #   logging.info('current current {} at {} {}'.format(current,xx,yy))
        if self.app.config['NoCurrents'] == '0':
            boat.vel += current

        side_dir = normalized_vector(
            make_vector(boat.dir[1], -boat.dir[0], boat.dir[2]))
        fwd_dir = normalized_vector(boat.dir)
        fwd_dp = dot_product(fwd_dir, normalized_vector(boat.vel))
        side_dp = dot_product(side_dir, normalized_vector(boat.vel))
        fwd_vel = fwd_dp * vector_len(boat.vel)
        side_vel = side_dp * vector_len(boat.vel)

        yaw_force = boat.rudder * (fwd_vel * 0.1 + 0.03)
        boat.dyaw += yaw_force

        boat.vel -= side_dir * side_vel * 0.05
        boat.vel -= fwd_dir * fwd_vel * 0.01
        boat.vel *= 0.9999  # boat.vel_fade
        if self.app.config['NoCurrents'] == '0':
            boat.vel -= current

        boat.yaw += boat.dyaw
        boat.pitch += boat.dpitch
        boat.roll += boat.droll

        boat.dyaw *= 0.2
        boat.dpitch *= 0.2
        boat.droll *= 0.2
