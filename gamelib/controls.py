from __future__ import print_function
from . import data
from .gui import *
from .menu import *
from .game import *

import logging
import pygame

def make_actions():
    actions = {}
    actions['W'] = False
    actions['w'] = False
    actions['s'] = False
    actions['a'] = False
    actions['d'] = False
    actions['c'] = False
    actions['b'] = False
    actions['anchor'] = False
    actions['enter'] = False

    actions['mus+'] = False
    actions['mus-'] = False
    actions['mus_toggle'] = False
    actions['mouse'] = False
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

        self.key_to_action[pygame.K_c] = 'c'
        self.key_to_action[pygame.K_b] = 'b'
        self.key_to_action['mouse'] = 'mouse'

        self.key_to_action[pygame.K_SPACE] = 'anchor'
        self.key_to_action[pygame.K_RETURN] = 'enter'

        self.key_to_action[pygame.K_PLUS] = 'mus+'
        self.key_to_action[pygame.K_KP_PLUS] = 'mus+'
        self.key_to_action[pygame.K_EQUALS] = 'mus+'
        self.key_to_action[pygame.K_MINUS] = 'mus-'
        self.key_to_action[pygame.K_KP_MINUS] = 'mus-'
        self.key_to_action[pygame.K_m] = 'mus_toggle'

    def onKey(self, key, isdown, actions):
        action = self.key_to_action.get(key, None)
        if not action:
            return
        actions[action] = isdown
