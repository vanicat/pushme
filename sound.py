import pygame
from pygame.locals import *

from const import *
from utils import *

def level_to_x(level):
    return 290 + 50*level



class Sound():
    def __init__(self, screen):
        background = pygame.Surface(screen.get_size()).convert()
        background.fill((250, 250, 250))
        label = font.default.render("Sound & Music", True, (0, 0, 0))
        rect = label.get_rect(midtop=SCREENRECT.midtop)
        background.blit(label,rect)

        musicy = (SCREENRECT.top + 2*SCREENRECT.centery)/3
        soundy = (SCREENRECT.bottom + 2*SCREENRECT.centery)/3

        labelx = SCREENRECT.left+30

        label = font.default.render("Music", True, (0, 0, 0))
        rect = label.get_rect(midleft=(labelx,musicy))
        background.blit(label,rect)

        label = font.default.render("Sound", True, (0, 0, 0))
        rect = label.get_rect(midleft=(labelx,soundy))
        background.blit(label,rect)

        label = font.default.render(".", True, (0, 0, 0))
        center_music = []
        center_sound = []

        for i in range(11):
            centerx = level_to_x(i)

            center = (centerx, soundy)
            center_sound.append(center)
            rect = label.get_rect(center=center)
            background.blit(label,rect)

            center = (centerx, musicy)
            center_music.append(center)
            rect = label.get_rect(center=center)
            background.blit(label,rect)

        self.center_music = center_music
        self.center_sound = center_sound
        self.screen = screen
        self.background = background
        Sound.fail = load_sound('failed.wav')
        Sound.lock = load_sound('success.wav')

        Sound.heroes_die = load_sound('die.wav')

        Sound.monster_die = load_sound('killing.wav')

        Sound.newlevel = load_sound('end-level.wav')

    def __call__(self):
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return 'quit'
