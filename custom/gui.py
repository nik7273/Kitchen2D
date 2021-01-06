"""
Author: Nikhil Devraj
Adapted from Kitchen2D: https://github.com/zi-w/Kitchen2D
"""

from Box2D import *
from Box2D.b2 import *
from env_constants import *

import pygame
import numpy as np

class guiWorld:
    def __init__(self, caption='PyBox2D Simulator', overclock=None):
        """
        Args:
            caption:  caption on the window
            overclock: number of frames to skip when showing graphical interface
        """
        self.screen = pygame.display.set_mode((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.overclock = overclock
        self.screen_origin = b2Vec2(SCREEN_WIDTH/2., TABLE_HEIGHT)
        self.colors = {
            'countertop': (50, 50, 50, 255),
            'gripper': (244, 170, 66, 255),
            'cup': (15, 0, 100, 0),
            'stirrer': (163, 209, 224, 255),
            'spoon': (73, 11, 61, 255),
            'obstacle': (123, 128, 120, 255),
            'sensor': (255, 255, 255, 20),
            #'sensor': (155, 155, 155, 255), # To visualize the sensor
            'default': (81, 81, 81, 255),
            'faucet': (175, 175, 175, 255),
            'water': (26, 130, 252),
            'block': (0, 99, 0),
            'coffee': (165, 42, 42),
            'cream': (225, 225, 225),
            'sugar': (255, 192, 203),
        }
