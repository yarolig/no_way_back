import numpy as np
import random
import math
import logging
from . import glboilerplate
from . import data
import pygame
import time

from OpenGL.GL import *

__all__ = ['Skybox']


def make_vector5(x=0, y=0, z=0, u=0, v=0):
    v = np.ndarray(shape=(3,), dtype=float)
    v[0] = x
    v[1] = y
    v[2] = z
    return v


class Skybox(object):
    def __init__(self):
        self.floats = []

    def prepare(self):
        cos = math.cos
        sin = math.sin
        arange = 8
        bhalfrange = 4
        r = 3000.0

        def alpha(q):
            return q * math.pi * 2.0 / arange

        def beta(q):
            return q * math.pi * 2.0 / arange

        def vertex(a, b):
            x = r * cos(alpha(a)) * cos(beta(b))
            y = r * sin(alpha(a)) * cos(beta(b))
            z = r * sin(beta(b))
            u = -float(a) / arange
            v = beta(float(math.fabs(float(b) / bhalfrange)))
            self.floats += [x, y, z, u, v * 5]

        for a in range(arange):
            for b in range(-1, bhalfrange + 1):
                vertex(a + 1, b)
                vertex(a, b)
                vertex(a, b + 1)
                vertex(a + 1, b + 1)
        self.vb = glboilerplate.VertexBuffer(
            self.floats,
            vertex_size=3, vertex_offset=0,
            uv_size=2, uv_offset=4 * 3, mode=GL_QUADS)
        self.vb.prepare()
        texpath = data.modelpath('mud_road_2k.jpg')
        from . import game
        self.texture = game.gettexture2d(texpath)

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        glEnable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)

        glEnable(GL_TEXTURE_2D)
        self.texture.bind()
        self.vb.draw()
        self.texture.unbind()
        glDepthMask(GL_TRUE)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
