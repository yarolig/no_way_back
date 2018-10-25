import numpy as np
import logging

import pygame

import ctypes
from OpenGL.GL import *
from OpenGL.GLU import *

class GlBoilerplateException(Exception):
    pass


class Texture(object):
    def __init__(self, filename):
        surface = pygame.image.load(filename)
        data = pygame.image.tostring(surface, 'RGBA', True)
        w, h = surface.get_size()

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA8, w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    def bind(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.id)

    @staticmethod
    def unbind():
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)


class Texture3D(object):
    def __init__(self, filenames):
        surfaces = []
        for filename in filenames:
            surfaces.append(pygame.image.load(filename))

        depth = len(filenames)

        h, w = 0, 0
        ph, pw = 0, 0
        data = None
        for s in surfaces:
            d = pygame.image.tostring(s, 'RGBA', True)
            data = d if not data else data + d
            w, h = s.get_size()
            if ph:
                assert ph == h and pw == w
            pw, ph = w, h

        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_3D, self.id)
        gluBuild3DMipmaps(GL_TEXTURE_3D, GL_RGBA8, w, h, depth, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    def bind(self):
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_TEXTURE_3D)
        glBindTexture(GL_TEXTURE_3D, self.id)

    @staticmethod
    def unbind():
        glBindTexture(GL_TEXTURE_3D, 0)
        glDisable(GL_TEXTURE_3D)


class VertexBuffer(object):
    def __init__(self, floats,
                 vertex_size=3, vertex_offset=0,
                 uv_size=0, uv_offset=0,
                 color_size=0, color_offset=0,
                 normal_size=0, normal_offset=0,
                 stride=None, mode=GL_TRIANGLES
                 ):
        if stride is None:
            stride = 4*(vertex_size + uv_size + color_size + normal_size)

        self.data = np.asanyarray(floats, dtype=np.float32)
        self.count = len(self.data)
        self.id = 0
        self.vertex_size = vertex_size
        self.vertex_offset = ctypes.c_void_p(vertex_offset)
        self.uv_size = uv_size
        self.uv_offset = ctypes.c_void_p(uv_offset)
        self.color_size = color_size
        self.color_offset = ctypes.c_void_p(color_offset)
        self.normal_size = normal_size
        self.normal_offset = ctypes.c_void_p(normal_offset)
        self.stride = stride
        self.mode = mode

    def prepare(self):
        self.id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        # print("{}".format(self.data[0:20]))
        glBufferData(GL_ARRAY_BUFFER, len(self.data)*4, self.data, GL_STATIC_DRAW)
        size = glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        if size != len(self.data) * 4:
            logging.error("Can't create VertexBuffer of size {}, got size {}".format(len(self.data) * 4, size))
            glDeleteBuffers(1, self.id)
            self.id = 0
            return False
        return True

    def draw(self):
        if not self.id:
            return

        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glEnableClientState(GL_VERTEX_ARRAY)

        if self.uv_size:
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glTexCoordPointer(self.uv_size, GL_FLOAT, self.stride, self.uv_offset)

        if self.normal_size:
            glEnableClientState(GL_NORMAL_ARRAY)
            glNormalPointer(GL_FLOAT, self.stride, self.normal_offset)

        if self.color_size:
            glEnableClientState(GL_COLOR_ARRAY)
            glColorPointer(self.color_size, GL_FLOAT, self.stride, self.color_offset)

        glVertexPointer(self.vertex_size, GL_FLOAT, self.stride,self.vertex_offset or None)

        glDrawArrays(self.mode, 0,  len(self.data) * 4 // self.stride)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def destroy(self):
        glDeleteBuffers(1, self.id)
