#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want from this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
import os.path, math
from pygame.locals import *

SCREENRECT     = Rect(0, 0, 1000, 700)

def load_image(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as error:
        print("Impossible de charger l'image : {0}", error)
        raise SystemExit, message
    image = image.convert_alpha()
    return image, image.get_rect()

class MovingAgent(pygame.sprite.Sprite):
    def __init__(self,containers):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image, self.rect = load_image(self.image_name)
        self.speed = 2

    def move(self,direction):
        if direction == 'up':
            self.rect.move_ip(0, direction*self.speed)
        elif direction == 'down':
            self.rect.move_ip(0, -direction*self.speed)
        elif direction == 'right':
            self.rect.move_ip(direction*self.speed, 0)
        else:
            self.rect.move_ip(-direction*self.speed, 0)

class Heroes(MovingAgent):
    def __init__(self):
        self.image_name = 'heroes.png'
        MovingAgent.__init__(self,self.containers)
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.direction = -math.pi/2
        self.posx = self.rect.centerx
        self.posy = self.rect.centery

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self,dir):
        self._direction = dir
        self.xspeed = math.cos(dir) * self.speed
        self.yspeed = math.sin(dir) * self.speed

    def update(self):
        self.posx += self.xspeed
        self.posy += self.yspeed
        self.rect.center = (int(self.posx),int(self.posy))

    def turn_right(self):
        self.direction += 0.1

    def turn_left(self):
        self.direction -= 0.1

class Monsters(MovingAgent):
    def __init__(self):
        self.image_name = 'monsters.png'
        MovingAgent.__init__(self,self.containers)

def main():
    pygame.init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Repeat keys
    pygame.key.set_repeat(100,100)

    background = pygame.Surface(screen.get_size()).convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0,0))
    pygame.display.flip()

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
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    player.turn_right()
                elif event.key == K_LEFT:
                    player.turn_left()
        keystate = pygame.key.get_pressed()

        # clear/erase the last drawn sprites
        visible.clear(screen, background)

        #update visible the sprites
        visible.update()

        #draw the scene
        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(40)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.time.wait(1000)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()
