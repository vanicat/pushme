import pygame
from pygame.locals import *

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)

PLROTATESPEED  = 2
BOTROTATESPEED = 1
ROTATESPEED    = 1
RANGE          = 200

MENUHEIGHT     = 70

class font:
    default = None
    menu = None
    highscore = None

def font_init():
    font.default = pygame.font.Font("data/font/Reality Hyper Regular.ttf",20)
    font.menu = pygame.font.Font("data/font/darktech_ldr.ttf",40)
    font.highscore = pygame.font.Font("data/font/Squares Bold Free.otf",40)
