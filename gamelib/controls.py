from __future__ import print_function
from . import data
from .gui import *
from .menu import *
from .game import *

import logging
import pygame


# too lazy to subclass a dict.
# It may be too challenging to support Python 2 and 3
def make_actions():
    actions = {}
    actions['w'] = False
    actions['s'] = False
    actions['a'] = False
    actions['d'] = False
    actions['anchor'] = False
    actions['enter'] = False
    return actions


class Controls(object):
    def __init__(self):
        self.key_to_action = {}

    def load_config(self):
        self.load_default_config()

    def load_default_config(self):
        self.key_to_action[pygame.K_UP] = 'w'
        self.key_to_action[pygame.K_DOWN] = 's'
        self.key_to_action[pygame.K_LEFT] = 'a'
        self.key_to_action[pygame.K_RIGHT] = 'd'

        self.key_to_action[pygame.K_w] = 'w'
        self.key_to_action[pygame.K_s] = 's'
        self.key_to_action[pygame.K_a] = 'a'
        self.key_to_action[pygame.K_d] = 'd'

        self.key_to_action[pygame.K_SPACE] = 'anchor'
        self.key_to_action[pygame.K_RETURN] = 'enter'

    def onKey(self, key, isdown, actions):
        action = self.key_to_action.get(key, None)
        if not action:
            return
        actions[action] = isdown
