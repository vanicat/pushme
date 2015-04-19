import pygame
from pygame.locals import *

import const

class Scoring(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.score = 0

    def collide(self,fst,snd):
        if fst.locked or snd.locked:
            self.score += 200
        else:
            self.score += 100

    def wall(self,dead):
        if dead.locked:
            self.score += 75
        else:
            self.score += 40

    def update(self):
        self.image = const.font.render("{}".format(self.score),True, (0,0,0,255))
        self.rect  = self.image.get_rect(midtop=const.SCREENRECT.midtop)
