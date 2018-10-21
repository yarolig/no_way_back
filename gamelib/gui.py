import logging
import pygame
import pygame.freetype
import time
from OpenGL import GL
from OpenGL import GLU


def drawText(position, textString, color=None):
    font = pygame.freetype.Font(None, 64)
    if color is None:
        color = pygame.Color('white')

    textSurface, rect = font.render(textString, fgcolor=color)
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    (x, y, z) = position
    GL.glRasterPos3d(x, y + 64 - textSurface.get_height(), z)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glDrawPixels(textSurface.get_width(),
                    textSurface.get_height(),
                    GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)
    del textSurface


class Button(object):
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.active = False

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
            drawText((self.x, self.y, 0), self.text, pygame.Color('yellow'))
        else:
            drawText((self.x, self.y, 0), self.text, pygame.Color('white'))


class Frame(object):
    def __init__(self):
        self.buttons = []
        self.ypos = 0

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
        self.ypos += 70
        b = Button(text, 60, 600 - self.ypos, 300, 65)
        if action:
            b.onclick = action
        self.buttons.append(b)
