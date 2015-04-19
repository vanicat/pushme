import pygame
from pygame.locals import *

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)

PLROTATESPEED  = 2
BOTROTATESPEED = 1
ROTATESPEED    = 1
RANGE          = 200

MENUHEIGHT     = 50

font = None
font_menu = None

def font_init():
    global font, font_menu
    font = pygame.font.Font("data/Comfortaa-Light.ttf",20)
    font_menu = font
