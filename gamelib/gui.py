import logging
import pygame
import pygame.freetype
import time
from OpenGL import GL
from OpenGL import GLU


def drawText(position, textString, color=None, pxsize=64):
    font = pygame.freetype.Font(None, pxsize)
    if color is None:
        color = pygame.Color('white')

    textSurface, rect = font.render(textString, fgcolor=color)
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    (x, y, z) = position

    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glRasterPos3d(x, y + pxsize - textSurface.get_height(), z)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glDrawPixels(textSurface.get_width(),
                    textSurface.get_height(),
                    GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)
    del textSurface


class Button(object):
    def __init__(self, text, x, y, w, h, pxsize):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.active = False
        self.pxsize = pxsize

    def click(self):
        if self.active:
            self.onclick()

    def onclick(self):
        pass

    def mouseMove(self, mx, my):
        x, y, w, h = self.x, self.y, self.w, self.h
        self.active = (x <= mx <= x + w) and (y <= my <= y + h)

    def draw(self):
        if self.active:
            drawText((self.x, self.y, 0),
                     self.text, pygame.Color('yellow'),
                     pxsize=self.pxsize)
        else:
            drawText((self.x, self.y, 0),
                     self.text,
                     pygame.Color('white'),
                     pxsize=self.pxsize)


class Frame(object):
    def __init__(self, app):
        self.buttons = []
        self.ypos = 0
        self.pxsize = 64
        self.app = app


    def click(self):
        for b in self.buttons:
            b.click()

    def mouseMove(self, mx, my):
        for b in self.buttons:
            b.mouseMove(mx, my)

    def draw(self):
        for b in self.buttons:
            b.draw()

    def addButton(self, text, action=None):
        self.ypos += int(self.pxsize * 1.1)
        w,h=self.app.get_screen_size()
        b = Button(text, 60, h - self.ypos, w/2, self.pxsize, self.pxsize)
        if action:
            b.onclick = action
        self.buttons.append(b)
