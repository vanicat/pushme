import pygame
from pygame.locals import *

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)

PLROTATESPEED  = 2
BOTROTATESPEED = 1
ROTATESPEED    = 1
RANGE          = 200
MONSTERSPEED   = 1.2

MENUHEIGHT     = 70

class font:
    default = None
    menu = None
    highscore = None

def font_init():
    font.default = pygame.font.Font("data/font/Squares Bold Free.otf",40)
    font.menu = font.default
    font.highscore = font.default
