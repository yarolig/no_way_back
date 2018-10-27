import logging
import pygame
import pygame.freetype
import time
from . import data
from OpenGL import GL
from OpenGL import GLU


def draw_text(position, text, color=None, pxsize=64):
    # font = pygame.freetype.Font(None, pxsize)
    font = pygame.freetype.Font(data.modelpath('dizhitl-regular.ttf'), pxsize)
    if color is None:
        color = pygame.Color('white')

    surface, rect = font.render(text, fgcolor=color)
    pixel_data = pygame.image.tostring(surface, "RGBA", True)
    (x, y, z) = position

    GL.glDisable(GL.GL_LIGHTING)
    GL.glDisable(GL.GL_DEPTH_TEST)
    GL.glRasterPos3d(x, y + pxsize - surface.get_height(), z)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glDrawPixels(surface.get_width(),
                    surface.get_height(),
                    GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixel_data)
    del surface


class Button(object):
    def __init__(self, text, x, y, w, h, pxsize):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.active = False
        self.pxsize = pxsize
        self.disabled = False
        self.color = pygame.Color('white')

    def click(self):
        if self.active:
            self.onclick()

    def onclick(self):
        pass

    def mouseMove(self, mx, my, app):
        if self.disabled:
            return
        x, y, w, h = self.x, app.get_screen_size()[1] - self.y, self.w, self.h
        self.active = (x <= mx <= x + w) and (y <= my <= y + h)

    def draw(self, app):
        color = self.color
        if self.disabled:
            color = pygame.Color('gray')
        elif self.active:
            color = pygame.Color('yellow')

        draw_text((self.x, app.get_screen_size()[1] - self.y, 0),
                  self.text, color,
                  pxsize=self.pxsize)


class Checkbox(Button):
    state = False

    def draw(self, app):
        t = self.text
        if self.state:
            self.text = "[V] " + self.text
        else:
            self.text = "[ ] " + self.text
        Button.draw(self, app)
        self.text = t

    def ontoggle(self):
        pass

    def onclick(self):
        self.state = not self.state
        self.ontoggle()


class VolumeBox(Button):
    value = 5
    maxvalue = 10

    def draw(self, app):
        self.text = ('[' +
                     '|' * self.value +
                     '.' * (self.maxvalue - self.value)
                     + ']')
        Button.draw(self, app)

    def inc(self):
        self.value = min(self.maxvalue, self.value + 1)
        self.onchange()

    def dec(self):
        print([0, self.value - 1])
        self.value = max(0, self.value - 1)
        self.onchange()

    def onchange(self):
        pass


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
            b.mouseMove(mx, my, self.app)

    def draw(self):
        for b in self.buttons:
            b.draw(self.app)

    def add_button(self, text, action=None, disabled=False):
        self.ypos += int(self.pxsize * 1.1)
        w, h = self.app.get_screen_size()
        b = Button(text, 60, self.ypos, w / 2, self.pxsize, self.pxsize)
        b.disabled = disabled
        if action:
            b.onclick = action
        self.buttons.append(b)
        return b

    def add_checkbox(self, text, action=None, state=False):
        self.ypos += int(self.pxsize * 1.1)
        w, h = self.app.get_screen_size()
        b = Checkbox(text, 60, self.ypos, w / 2, self.pxsize, self.pxsize)
        b.state = state
        if action:
            b.ontoggle = action
        self.buttons.append(b)
        return b

    def add_volumebox(self, text="", action=None, value=5, maxvalue=10):
        self.ypos += int(self.pxsize * 1.1)
        w, h = self.app.get_screen_size()
        b = VolumeBox(text, 60, self.ypos, w / 2, self.pxsize, self.pxsize)
        b.value = value
        b.maxvalue = maxvalue
        if action:
            b.onclick = action
        self.buttons.append(b)
        return b
