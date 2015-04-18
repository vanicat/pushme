#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want from this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
import os.path
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

    def alive(self):
        return True

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

    background = pygame.Surface(screen.get_size()).convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0,0))
    pygame.display.flip()

    monsters = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    visible = pygame.sprite.RenderUpdates()

    Heroes.containers = [visible]
    Monsters.containers = [visible,monsters]

    player = Heroes()
    Monsters()

    clock = pygame.time.Clock()
    while player.alive():
        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
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
