import pygame
from pygame.locals import *

import const
import bisect

class Item(pygame.sprite.Sprite): # not sprite...
    def __init__(self,width,pos,score):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.image = pygame.Surface((width,const.MENUHEIGHT),flags=SRCALPHA).convert_alpha()
        self.image.fill((255, 255, 255, 0))

        rectimage = self.image.get_rect()

        labelnum = const.font_menu.render("{}:".format(pos), True, (0,0,0,255))
        rect = labelnum.get_rect(midleft=rectimage.midleft)
        self.image.blit(labelnum,rect)

        labelscore = const.font_menu.render("{}".format(score), True, (0,0,0,255))
        rect = labelscore.get_rect(midright=rectimage.midright)
        self.image.blit(labelscore,rect)

        self.rect = self.image.get_rect(midtop=const.SCREENRECT.midtop)
        self.rect.move_ip(0,pos * const.MENUHEIGHT)


class Highscore():
    def __init__(self):
        self.scores = []

    def add(self,score):
        bisect.insort(self.scores, score)

    def __iter__(self):
        return enumerate(self.scores)

highscore = Highscore()

def call(screen,score):
    highscore.add(score)

    background = pygame.Surface(screen.get_size()).convert()
    # imgbg = load_image('background-menu.png')
    background.fill((250, 250, 250))
    #background.blit(imgbg,(0,0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    # Groups of sprite
    visible = pygame.sprite.RenderUpdates()

    Item.containers = visible

    for i, s in highscore:
        Item(screen.get_width()/2,i+1,s)
    # a clock
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or \
               event.type == KEYDOWN or \
               event.type == JOYBUTTONDOWN:
                return

        visible.clear(screen, background)

        visible.update()

        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(60)
