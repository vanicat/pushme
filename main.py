#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want from this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
from pygame.locals import *
import os.path, math


SCREENRECT     = Rect(0, 0, 1000, 700)
ROTATESPEED    = 1
RANGE          = 200

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
    def __init__(self, containers, **kwargs):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.rect = self.src_image.get_rect(**kwargs)
        self.width = self.rect.width
        self.height = self.rect.height
        self.image = pygame.Surface((self.width,self.height),flags=SRCALPHA).convert_alpha()

        self.posx = self.rect.centerx
        self.posy = self.rect.centery

    def _adapt_direction(self):
        self.image.fill((0,0,0,0))
        image = pygame.transform.rotate(self.src_image,-self.direction)
        rec = image.get_rect()
        xdec = (rec.width-self.width)/2
        ydec = (rec.height-self.height)/2
        self.image.blit(image, (0,0),(xdec,ydec,xdec+self.width,ydec+self.height)) # Could use dirty sprite for this
        self.xdir = math.cos(math.radians(self.direction))
        self.ydir = math.sin(math.radians(self.direction))

    def update(self):
        self.move_to(self.posx + self.xdir * self.speed,
                     self.posy + self.ydir * self.speed)

    def move_to(self,x,y):
        self.posx = x
        self.posy = y
        self.rect.center = (int(x),int(y))

    def dist(self,other):
        return math.sqrt((other.posx-self.posx)**2 + (other.posy-self.posy)**2)


class Heroes(MovingAgent):
    def __init__(self, targets):
        MovingAgent.__init__(self,self.containers,midbottom=SCREENRECT.midbottom)

        self.targets = targets

        self.direction = -90
        self.speed = 2
        self._adapt_direction()

        self.accelerating = 0
        self.turning = 0

        self.locked = None

    def turn_right(self):
        self.turning = ROTATESPEED

    def turn_left(self):
        self.turning = -ROTATESPEED

    def no_turn(self):
        self.turning = 0

    def accelerate(self):
        self.accelerating = .1

    def brake(self):
        self.accelerating = -.1

    def no_accel(self):
        self.accelerating = 0

    def update(self):
        self.speed += self.accelerating
        if self.turning:
            self.direction += self.turning
            self._adapt_direction()

        MovingAgent.update(self)


    def lock(self):
        def thrd(x):
            x[2]

        in_range = []
        for target in self.targets:
            dist1 = (target.posx-self.posx)*self.ydir - (target.posy-self.posy)*self.xdir
            dist2 = target.dist(self)
            if abs(dist1) < target.height and dist2 > 0 and dist2 < RANGE:
                in_range.append((target,dist1,dist2))
        if not in_range: return
        locked = min(in_range,key=thrd)
        self.locked = locked[0]
        locked[0].lock(self,locked[2],locked[1] > 0)

    def unlock(self):
        if self.locked:
            self.locked.unlock()
            self.locked = None


    def __call__(self,action):
        self.action[action]()

    def __contains__(self,action):
        return action in self.action

class Monsters(MovingAgent):
    def __init__(self):
        MovingAgent.__init__(self, self.containers)

        self.direction = 0
        self.speed = 1
        self._adapt_direction()
        self.locked = None

    def update(self):
        if self.locked:
            locked = self.locked
            self.direction = locked.direction + self.rotate
            self.move_to(locked.posx + locked.xdir * self.distance,
                         locked.posy + locked.ydir * self.distance)
            self._adapt_direction()
        else:
            MovingAgent.update(self)

    def lock(self, player, distance, direct):
        self.locked = player
        self.distance = distance
        if direct:
            self.rotate = 90
        else:
            self.rotate = -90

    def unlock(self):
        self.locked = None

def main():
    pygame.init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

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

    # images
    Heroes.src_image = load_image('heroes.png')
    Monsters.src_image = load_image('monsters.png')

    # The actors
    player = Heroes(monsters)
    Monsters().move_to(0,80)

    # a clock
    clock = pygame.time.Clock()

    action = {
        K_RIGHT: player.turn_right,
        K_LEFT: player.turn_left,
        K_DOWN: player.brake,
        K_UP: player.accelerate,
        K_SPACE: player.lock,
    }

    stoping = {
        K_RIGHT: player.no_turn,
        K_LEFT: player.no_turn,
        K_DOWN: player.no_accel,
        K_UP: player.no_accel,
        K_SPACE: player.unlock,
    }

    while player.alive():
        #get input
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            elif event.type == KEYDOWN and event.key in action:
                action[event.key]()
            elif event.type == KEYUP and event.key in stoping:
                stoping[event.key]()

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
