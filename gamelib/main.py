from __future__ import print_function
from . import data


import logging
import pygame
import time
from OpenGL import GL
from OpenGL import GLU


class App(object):
    def init(self):
        logging.basicConfig(level=logging.DEBUG)

        logging.debug("mixer pre-init")
        pygame.mixer.pre_init()
        #logging.debug("pygame.init")
        #pygame.init()

        logging.debug("display.init")
        pygame.display.init()

        logging.debug("set_mode")
        pygame.display.set_mode(
            [800, 600],
            pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)

        logging.debug("mixer init")
        pygame.mixer.init(frequency=44100, buffer=1024)
        logging.debug("mixer init: {}".format(pygame.mixer.get_init()))

        music_file = data.musicpath("Podington_Bear_-_11_-_Massive_Attack.ogg")
        logging.debug("music file: {}".format(music_file))

        self.music = pygame.mixer.Sound(music_file)
        self.music.play(loops=-1)


    def draw(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        GL.glClearColor(0.5, 0.6, 0.7, 1.0)
        pygame.display.flip()


    def mainloop(self):
        while True:
            for e in pygame.event.get():

                if e.type == pygame.QUIT:
                    return
                if e.type == pygame.KEYUP:
                    logging.debug("event {}".format(e))
                    if e.key == pygame.K_q:
                        self.music.fadeout(500)
                        time.sleep(0.5)
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
            self.draw()
            time.sleep(0.001)


def main():
    app = App()
    app.init()
    app.mainloop()
    print("Hello from your game's main()")
    print(data.load('sample.txt').read())
