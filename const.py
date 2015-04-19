import pygame
from pygame.locals import *

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)

PLROTATESPEED  = 4
BOTROTATESPEED = 1
ROTATESPEED    = 4
RANGE          = 100
MONSTERSPEED   = 1.2

MENUHEIGHT     = 70
LINEHEIGHT     = 35

class font:
    default = None
    menu = None
    highscore = None

def font_init():
    font.default = pygame.font.Font("data/font/Squares Bold Free.otf",40)
    font.small = pygame.font.Font("data/font/Squares Bold Free.otf",20)
    font.other = pygame.font.Font("data/font/Reality Hyper Regular.ttf",50)
    font.menu = font.default
    font.highscore = font.default
