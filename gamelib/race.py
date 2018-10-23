import numpy as np
import random
import math
import logging

import pygame
import time
import noise

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
CELL_SUBDIVIDE_SQUARED = CELL_SUBDIVIDE**2
CELL_SIDE = 10.0
VERTEX_COMPONENTS = (3 + 3 + 3)  # (vertices+normal+uvw)
VERTEX_SIZE = 4 * VERTEX_COMPONENTS  # sizeof(float)


class VertexBuffer(object):
    def __init__(self, size):
        self.data = [] #np.array(size=size, dtype='float32')
        self.id = 0

    def prepare(self):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, data, GL_STATIC_DRAW)

    def draw(self):
        pass

    def destroy(self):
        glDeleteBuffers(1, self.id)


class Race(object):
    def __init__(self):
        self.vb = None
        self.w = 0
        self.h = 0
        self.startpos = (0,0)
        self.checkpoints = []
        self.bouys = []
        self.fzcache = None

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

    def small_positive_noise(self,x,y):
        return math.fabs(noise.pnoise3(
                    float(x) / self.w,
                    float(y) / self.h,
                    1.2,
                    octaves=6, persistence=0.84123, lacunarity=2.41212,
                    repeatx=1, repeaty=1, repeatz=1,
                    base=1))

    def my_noise(self,x,y):
        return noise.pnoise3(
                    float(x*10) / self.w,
                    float(y*10) / self.h,
                    1.2,
                    octaves=5, persistence=0.54123, lacunarity=2.81212,
                    repeatx=10, repeaty=10, repeatz=1,
                    base=4)
    def getz(self,x,y):
        z = self.heightmap[int(x)%self.w][int(y)%self.h]
        return z


    def getfz(self,x,y):
        z = self.heightmap[int(x)%self.w][int(y)%self.h]
        if math.fabs(z) < 5.0:
            return z

        if not self.fzcache:
            self.fzcache = {}
        elem = self.fzcache.get((x,y))
        if elem:
            return elem
        else:
            z = self.my_noise(x,y) + z
            self.fzcache[(x,y)]=z
            return z

    def getz_noised(self,x,y):
        z = self.heightmap[int(x)%self.w][int(y)%self.h]
        if z > 0.5:
            k = 1 #k = z - 1 if z - 1 < 1 else 1
            z += k*10*self.small_positive_noise(x,y)
        elif z < 0.5:
            k = 1
            z += k*-10*self.small_positive_noise(x,y)
        return z

    @for_color(pygame.Color(255, 255, 0))
    def sand(self, x, y):
        self.heightmap[x][y] = 1
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(0, 128, 0))
    def hills(self, x, y):
        self.heightmap[x][y] = 20
        self.noisemap[x][y] = 10

    @for_color(pygame.Color(255, 0, 0))
    def start(self, x, y):
        self.heightmap[x][y] = self.heightmap[x-1][y]
        self.noisemap[x][y] = 0
        self.startpos = (x,y)

    @for_color(pygame.Color(128, 0, 0))
    def checkpoint(self, x, y):
        self.heightmap[x][y] = self.heightmap[x-1][y]
        self.noisemap[x][y] = 0
        self.checkpoints.append((x,y))

    @for_color(pygame.Color(0, 0, 0))
    def mountains(self, x, y):
        self.heightmap[x][y] = 300
        self.noisemap[x][y] = 100

    @for_color(pygame.Color(128, 128, 128))
    def wall(self, x, y):
        self.heightmap[x][y] = 10
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(0, 255, 255))
    def lake(self, x, y):
        self.heightmap[x][y] = -10
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(255, 128, 0))
    def buoy(self, x, y):
        self.heightmap[x][y] = self.heightmap[x-1][y]
        self.noisemap[x][y] = 0
        self.bouys.append((x,y))

    @for_color(pygame.Color(0, 0, 128))
    def ocean(self, x, y):
        self.heightmap[x][y] = -100
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(0, 0, 255))
    def sea(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(128, 255, 128))
    def sink(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(255, 0, 255))
    def curl(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0

    @for_color(pygame.Color(255, 128, 128))
    def fountain(self, x, y):
        self.heightmap[x][y] = -50
        self.noisemap[x][y] = 0

    def noise_heightmap(self):
        w= self.w
        h=self.h
        new_heightmap = np.ndarray(shape=(w,h), dtype=float)
        for y in range(h):
            for x in range(w):

                if (math.fabs(self.heightmap[x][y]) <= 1.0
                  or x == 0 or y == 0
                  or x == w-1 or y == h - 1):
                    new_heightmap[x][y] = self.heightmap[x][y]
                else:
                    new_heightmap[x][y] = self.getz_noised(x,y)
        self.heightmap = new_heightmap

    def soften_heightmap(self):
        w= self.w
        h=self.h
        new_heightmap = np.ndarray(shape=(w,h), dtype=float)
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
                    for dx,dy in dirs:
                        sum += self.getz(x+dx, y+dy)
                    new_heightmap[x][y] = sum/len(dirs)
        self.heightmap = new_heightmap

    def load(self, name):
        img = pygame.image.load(name)
        w, h = img.get_size()
        self.w = w
        self.h = h

        self.heightmap = np.ndarray(shape=(w,h), dtype=float)
        self.noisemap = np.ndarray(shape=(w,h), dtype=float)

        self.vb = VertexBuffer(size=w * h * CELL_SUBDIVIDE_SQUARED * VERTEX_SIZE)
        for y in range(h):
            for x in range(w):
                c = hc(img.get_at((y, x)))
                f = color_actions.get(c)
                if f:
                    #print("{} {} {} {}".format(f, c,x,y))
                    f(self, x, y)
                else:
                    color_actions[c] = lambda s, x, y: None
                    logging.warn('Please add @for_color(pygame.Color{})'.format(c))

        self.noise_heightmap()
        for i in range(5):
             logging.info('softening heightmap')
             self.soften_heightmap()
        #self.noise_heightmap()

if __name__ == '__main__':
    r = Race()
    r.load('../data/race1.png')
