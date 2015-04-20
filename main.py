#!/usr/bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want with this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
try:
    import pygame._view
except ImportError:
    pass
from pygame.locals import *

import os.path

from const import *
import menu
import game
import highscore


def main():
    pygame.init()

    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    pygame.mixer.music.load('data/tchtada.ogg')
    pygame.mixer.music.play(-1)

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if joysticks:
        joystick=joysticks[0]
        joystick.init()


    font_init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    thegame = game.Game(screen)

    todo = menu.menu(screen)
    while todo != 'quit':
        if todo == 'play':
            score = thegame()
            highscore.call(screen,score)
        elif todo == 'score':
            highscore.call(screen,None)
        todo = menu.menu(screen)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()
