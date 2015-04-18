#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want from this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
from pygame.locals import *
import os.path, math


SCREENRECT     = Rect(0, 0, 1000, 700)
ROTATESPEED    = 10

def load_image(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as error:
        print("Impossible de charger l'image : {0}", error)
        raise SystemExit, message
    image = image.convert_alpha()
    return image

class MovingAgent(pygame.sprite.Sprite):
    def __init__(self, image_name, containers, **kwargs):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.image_name = image_name
        self.src_image = load_image(self.image_name)
        self.rect = self.src_image.get_rect(**kwargs)
        self.width = self.rect.width
        self.height = self.rect.height
        self.image = pygame.Surface((self.width,self.height),flags=SRCALPHA).convert_alpha()

        self.posx = self.rect.centerx
        self.posy = self.rect.centery

    def _adapt_direction(self):
        image = pygame.transform.rotate(self.src_image,-self.direction)
        rec = image.get_rect()
        xdec = (rec.width-self.width)/2
        ydec = (rec.height-self.height)/2
        self.image.blit(image, (0,0),(xdec,ydec,xdec+self.width,ydec+self.height))
        self.xdir = math.cos(math.radians(self.direction))
        self.ydir = math.sin(math.radians(self.direction))

    def update(self):
        self.posx += self.xdir * self.speed
        self.posy += self.ydir * self.speed
        self.rect.center = (int(self.posx),int(self.posy))


class Heroes(MovingAgent):
    def __init__(self):
        MovingAgent.__init__(self,'heroes.png',self.containers,midbottom=SCREENRECT.midbottom)

        self.direction = -90
        self.speed = 2
        self._adapt_direction()

        self.action = {
            K_RIGHT: self.turn_right,
            K_LEFT: self.turn_left,
            K_DOWN: self.brake,
            K_UP: self.accelerate,
        }

    def turn_right(self):
        self.direction += ROTATESPEED
        self._adapt_direction()

    def turn_left(self):
        self.direction -= ROTATESPEED
        self._adapt_direction()

    def accelerate(self):
        self.speed += .1

    def brake(self):
        self.speed -= .1

    def __call__(self,action):
        self.action[action]()

    def __contains__(self,action):
        return action in self.action

class Monsters(MovingAgent):
    def __init__(self):
        MovingAgent.__init__(self,'monsters.png',self.containers)

        self.direction = 0
        self.speed = 1
        self._adapt_direction()

def main():
    pygame.init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Repeat keys
    pygame.key.set_repeat(100,100)

    # Set background
    background = pygame.Surface(screen.get_size()).convert()
    imgbg = load_image('background.png')
    background.fill((250, 250, 250))
    #background.blit(imgbg,(0,0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    # Groups of sprite
    monsters = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    visible = pygame.sprite.RenderUpdates()

    Heroes.containers = visible
    Monsters.containers = visible, monsters

    # The actors
    player = Heroes()
    Monsters()

    # a clock
    clock = pygame.time.Clock()

    while player.alive():
        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            elif event.type == KEYDOWN and event.key in player:
                player(event.key)

        # clear/erase the last drawn sprites
        visible.clear(screen, background)

        #update visible the sprites
        visible.update()

        #draw the scene
        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(60)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()
