import pygame
from pygame.locals import *

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)

PLROTATESPEED  = 2
BOTROTATESPEED = 1
ROTATESPEED    = 1
RANGE          = 200

font = None

def font_init():
    global font
    font = pygame.font.Font("data/Comfortaa-Light.ttf",20)
