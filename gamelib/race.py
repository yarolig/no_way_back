import numpy as np
import random
import math
import logging

import pygame
import time
import noise
import json
import os

from OpenGL.GL import *
from OpenGL.GLU import *

try:
    from .data import *
    import objloader
except:
    pass

color_actions = {}


def hc(color):
    return (color.r, color.g, color.b)


def for_color(color):
    def decorator(func):
        color_actions[hc(color)] = func
        print('{} {}'.format(hc(color), repr(func)))

    return decorator


#


def pargs(func):
    def wrapper(*args, **kwargs):
        print("pargs {} {}".format(args, kwargs))
        return func(*args, **kwargs)

    return wrapper


CELL_SUBDIVIDE = 4
CELL_SUBDIVIDE_SQUARED = CELL_SUBDIVIDE ** 2
CELL_SIDE = 10.0
VERTEX_COMPONENTS = (3 + 3 + 3)  # (vertices+normal+uvw)
VERTEX_SIZE = 4 * VERTEX_COMPONENTS  # sizeof(float)


class VertexBuffer(object):
    def __init__(self, size):
        self.data = []  # np.array(size=size, dtype='float32')
        self.id = 0

    def prepare(self):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def draw(self):
        pass

    def destroy(self):
        glDeleteBuffers(1, self.id)


A_SINK = 1
A_SOURCE = 2
A_CURL = 3
A_FOUNTAIN = 4
A_GEYSER = 5
A_BUBBLE_SINK = 5
A_GEYSER = 5


class Anomaly(object):
    def __init__(self, x, y, force=1.0, range=10):
        self.x = x
        self.y = y
        self.force = force
        self.range = range

    def pos_for_debris(self, scale):
        a = random.randint(0, 999)
        r = scale * self.range * 0.8 * (0.001 * random.randint(1, 1000))  # ** 0.5
        x = r * math.cos(a)
        y = r * math.sin(a)
        z = 0
        return (self.x * scale + x,
                self.y * scale + y, z)


class SinkAnomaly(Anomaly):
    value_multiplier = 1.0

    def anomaly(self, x, y):
        d = (self.x - x, self.y - y)
        distance = (d[0] ** 2 + d[1] ** 2) ** 0.5
        if distance < 0.001:
            return (0.0, 0.0)
        if distance > self.range:
            return (0.0, 0.0)
        direction = (d[0] / distance, d[1] / distance)
        value = self.value_multiplier * self.force
        return (direction[0] * value - 0.01 * direction[1] * value,
                direction[1] * value + 0.01 * direction[0] * value)


class SourceAnomaly(SinkAnomaly):
    value_multiplier = -1.0


class CurlAnomaly(Anomaly):
    value_multiplier = 1.0

    def anomaly(self, x, y):
        d = (self.x - x, self.y - y)
        distance = (d[0] ** 2 + d[1] ** 2) ** 0.5
        if distance < 0.001:
            return (0.0, 0.0)
        if distance > self.range:
            return (0.0, 0.0)
        direction = (d[0] / distance, d[1] / distance)
        value = self.value_multiplier * self.force
        return (-direction[1] * value, direction[0] * value)


class Race(object):
    def __init__(self):
        self.vb = None
        self.w = 0
        self.h = 0
        self.startpos = (0, 0)
        self.checkpoints = []
        self.endpoints = []
        self.bouys = []
        self.boats = []
        self.fzcache = None
        self.anomalies = []

    def vbset(self, x, y, n, vz, vx=None, vy=None, normal=None, tex=None):
        assert 0 <= n < CELL_SUBDIVIDE ** 2
        assert 0 <= x <= self.w
        assert 0 <= y <= self.h
        if vx is None or vy is None:
            nx = n % CELL_SUBDIVIDE
            ny = n // CELL_SUBDIVIDE
            vx = x * CELL_SIDE + float(nx) / (CELL_SUBDIVIDE - 1) * CELL_SIDE
            vy = y * CELL_SIDE + float(ny) / (CELL_SUBDIVIDE - 1) * CELL_SIDE
        idx = ((x + y * self.w) * CELL_SUBDIVIDE + n) * VERTEX_COMPONENTS
        self.vb.data[idx + 0] = vx
        self.vb.data[idx + 1] = vy
        self.vb.data[idx + 2] = vz

    def small_positive_noise(self, x, y):
        return math.fabs(noise.pnoise3(
            float(x) / self.w,
            float(y) / self.h,
            1.2,
            octaves=6, persistence=0.84123, lacunarity=2.41212,
            repeatx=1, repeaty=1, repeatz=1,
            base=1))

    def my_noise(self, x, y):
        return noise.pnoise3(
            float(x * 10) / self.w,
            float(y * 10) / self.h,
            1.2,
            octaves=5, persistence=0.54123, lacunarity=2.81212,
            repeatx=10, repeaty=10, repeatz=1,
            base=4)

    def getz(self, x, y):
        z = self.heightmap[int(x) % self.w][int(y) % self.h]
        return z

    def getfz2(self, x, y):
        z = self.heightmap[int(x) % self.w][int(y) % self.h]
        z = self.my_noise(x, y) + z
        return z

    def getfz(self, x, y):
        z = self.heightmap[int(x) % self.w][int(y) % self.h]
        if math.fabs(z) < 5.0:
            return z

        if not self.fzcache:
            self.fzcache = {}
        elem = self.fzcache.get((x, y))
        if elem:
            return elem
        else:
            z = self.my_noise(x, y) + z
            self.fzcache[(x, y)] = z
            return z

    def getz_noised(self, x, y):
        z = self.heightmap[int(x) % self.w][int(y) % self.h]
        n = self.noisemap[int(x) % self.w][int(y) % self.h]
        if z > 0.5:
            k = 1  # k = z - 1 if z - 1 < 1 else 1
            z += k * n * self.small_positive_noise(x, y)
        elif z < 0.5:
            k = 1
            z += k * -n * self.small_positive_noise(x, y)
        return z

    @for_color(pygame.Color(255, 255, 0))
    def sand(self, x, y):
        self.heightmap[x][y] = 1
        self.noisemap[x][y] = 0.1

    @for_color(pygame.Color(0, 128, 0))
    def hills(self, x, y):
        self.heightmap[x][y] = 30
        self.noisemap[x][y] = 10

    @for_color(pygame.Color(255, 0, 0))
    def start(self, x, y):
        self.heightmap[x][y] = self.heightmap[x - 1][y]
        self.noisemap[x][y] = 0
        self.startpos = (x, y)

    @for_color(pygame.Color(128, 0, 0))
    def checkpoint(self, x, y):
        self.heightmap[x][y] = self.heightmap[x - 1][y]
        self.noisemap[x][y] = 0
        self.checkpoints.append((x, y))

    @for_color(pygame.Color(255, 127, 127))
    def endpoint(self, x, y):
        self.heightmap[x][y] = self.heightmap[x - 1][y]
        self.noisemap[x][y] = 0
        self.endpoints.append((x, y))

    @for_color(pygame.Color(0, 0, 0))
    def mountains(self, x, y):
        self.heightmap[x][y] = 300
        self.noisemap[x][y] = 100

    @for_color(pygame.Color(192, 192, 192))
    def rough(self, x, y):
        self.heightmap[x][y] = 50
        self.noisemap[x][y] = 50

    @for_color(pygame.Color(128, 128, 128))
    def wall(self, x, y):
        self.heightmap[x][y] = 20
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(0, 255, 255))
    def lake(self, x, y):
        self.heightmap[x][y] = -10
        self.noisemap[x][y] = 10.0

    @for_color(pygame.Color(255, 128, 0))
    def buoy(self, x, y):
        self.heightmap[x][y] = self.heightmap[x - 1][y]
        self.noisemap[x][y] = 0
        self.bouys.append((x, y))

    @for_color(pygame.Color(0, 255, 0))
    def boat(self, x, y):
        self.heightmap[x][y] = self.heightmap[x - 1][y]
        self.noisemap[x][y] = 0
        self.boats.append((x, y))

    @for_color(pygame.Color(0, 0, 128))
    def ocean(self, x, y):
        self.heightmap[x][y] = -100
        self.noisemap[x][y] = 50.0

    @for_color(pygame.Color(0, 0, 255))
    def sea(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 25.0

    @for_color(pygame.Color(128, 255, 128))
    def sink(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0
        a = SinkAnomaly(x, y)
        a.range = 40
        self.anomalies.append(a)

    @for_color(pygame.Color(255, 0, 255))
    def curl(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0
        a = CurlAnomaly(x, y)
        a.range = 40
        self.anomalies.append(a)

    @for_color(pygame.Color(255, 128, 128))
    def fountain(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0
        a = SourceAnomaly(x, y)
        a.range = 30
        self.anomalies.append(a)

    def noise_heightmap(self):
        w = self.w
        h = self.h
        new_heightmap = np.ndarray(shape=(w, h), dtype=float)
        for y in range(h):
            for x in range(w):

                if (math.fabs(self.heightmap[x][y]) <= 1.0
                    or x == 0 or y == 0
                    or x == w - 1 or y == h - 1):
                    new_heightmap[x][y] = self.heightmap[x][y]
                else:
                    new_heightmap[x][y] = self.getz_noised(x, y)
        self.heightmap = new_heightmap

    def soften_heightmap(self):
        w = self.w
        h = self.h
        new_heightmap = np.ndarray(shape=(w, h), dtype=float)
        dirs = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1),
            (-1, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (0, 0),
        ]
        for y in range(h):
            for x in range(w):
                if self.heightmap[x][y] <= 0:
                    new_heightmap[x][y] = self.heightmap[x][y]
                else:
                    sum = 0.0
                    for dx, dy in dirs:
                        sum += self.getz(x + dx, y + dy)
                    new_heightmap[x][y] = sum / len(dirs)
        self.heightmap = new_heightmap

    def enum_currents(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            sum = np.ndarray(shape=(2,), dtype=float)
            if self.heightmap[x][y] >= 100.3:
                pass
            else:
                for an in self.anomalies:
                    yield an.anomaly(x, y)

    def get_current(self, x, y):
        sum = np.ndarray(shape=(2,), dtype=float)
        for (x, y) in self.enum_currents(x, y):
            sum += (x, y)
        result = np.ndarray(shape=(3,), dtype=float)
        result[0] = sum[0]
        result[1] = sum[1]
        result[2] = 0
        return result

    def calc_currents(self):
        return
        w = self.w
        h = self.h
        for y in range(h):
            for x in range(w):
                if self.heightmap[x][y] <= -0.3:
                    self.currents[x][y][0] = 0
                    self.currents[x][y][1] = 0
                else:
                    for an in self.anomalies:
                        self.currents[x][y] += an.anomaly(x, y)

    def save_default_race_conf(self, name):
        self.save_race_conf({
            "scale_x": "20.0",
            "scale_y": "20.0",
            "scale_z": "2.0",
            "biome": "default",
            "prenoise": "1",
            "smooth": "2",
            "postnoise": "1",
            "next_races": "lake",
            "intro": "This is a simple race, nothing unusual",
            "outro": "Race completed!",

            "start_time": "30",
            "cp_time": "15",
            "type" : 'countup',  #"type" : 'checkpoints'

            "placeholder1": "1.0",
            "placeholder2": "1.0"
        }, name)

    def save_race_conf(self, cfg, name):
        s = json.dumps(cfg, indent=2)
        f = open(name, 'w')
        f.write(s)
        f.close()

    def load_race_conf(self, name):
        # if not os.path.exists(name):
        #    pass

        self.save_default_race_conf(name)

        f = json.load(open(name))
        self.config = f
        self.sx = float(self.config['scale_x'])
        self.sy = float(self.config['scale_y'])
        self.sz = float(self.config['scale_z'])
        self.prenoise = int(self.config['prenoise'])
        self.smooth = int(self.config['smooth'])
        self.postnoise = int(self.config['postnoise'])

    def load(self, name):
        self.load_race_conf(name.replace('.png', '.json'))
        img = pygame.image.load(name)
        w, h = img.get_size()
        self.w = w
        self.h = h

        self.heightmap = np.ndarray(shape=(w, h), dtype=float)
        self.noisemap = np.ndarray(shape=(w, h), dtype=float)
        self.currents = np.ndarray(shape=(w, h, 2), dtype=float)

        self.vb = VertexBuffer(size=w * h * CELL_SUBDIVIDE_SQUARED * VERTEX_SIZE)
        for y in range(h):
            for x in range(w):
                c = hc(img.get_at((x, h - y - 1)))
                f = color_actions.get(c)
                if f:
                    f(self, x, y)
                else:
                    color_actions[c] = lambda s, x, y: None
                    logging.warn('Please add @for_color(pygame.Color{})'.format(c))
        logging.info('calculating currents')
        self.calc_currents()

        for i in xrange(self.prenoise):
            logging.info('noising')
            self.noise_heightmap()

        for i in xrange(self.smooth):
            logging.info('bluring')
            self.soften_heightmap()

        for i in xrange(self.postnoise):
            logging.info('noising')
            self.noise_heightmap()


if __name__ == '__main__':
    r = Race()
    r.load('../data/race1.png')
