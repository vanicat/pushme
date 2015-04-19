import pygame
from pygame.locals import *
import math

from const import *

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
        self.dirx = math.cos(math.radians(self.direction))
        self.diry = math.sin(math.radians(self.direction))

    def turn_right(self):
        self.turning = self.rotatespeed

    def turn_left(self):
        self.turning = -self.rotatespeed

    def no_turn(self):
        self.turning = 0

    def update(self):
        if self.turning:
            self.direction += self.turning
            self._adapt_direction()
        self.move_to(self.posx + self.dirx * self.speed,
                     self.posy + self.diry * self.speed)

    def move_to(self,x,y):
        self.posx = x
        self.posy = y
        self.rect.center = (int(x),int(y))

    def center(self):
        self.move_to(SCREENRECT.centerx, SCREENRECT.centery)

    def dist(self,other):
        return math.sqrt((other.posx-self.posx)**2 + (other.posy-self.posy)**2)


class Heroes(MovingAgent):
    def __init__(self, targets):
        MovingAgent.__init__(self,self.containers)

        self.rotatespeed = PLROTATESPEED

        self.targets = targets

        self.direction = -90
        self.speed = 2
        self._adapt_direction()

        self.accelerating = 0
        self.turning = 0

        self.locked = pygame.sprite.GroupSingle()


    def turn(self, value):
        self.turning = self.rotatespeed * value

    def accel(self, value):
        self.accelerating = .1 * value

    def accelerate(self):
        self.accelerating = .1

    def brake(self):
        self.accelerating = -.1

    def no_accel(self):
        self.accelerating = 0

    def update(self):
        self.speed += self.accelerating

        MovingAgent.update(self)

    def kill(self):
        self.die_sound.play()
        MovingAgent.kill(self)

    def lock(self):
        def thrd(x):
            x[2]

        if self.locked.sprite:
            self.locked.sprite.unlock()
            self.locked.remove(self.locked.sprite)
            return

        in_range = []
        for target in self.targets:
            dist1 = (target.posx-self.posx)*self.diry - (target.posy-self.posy)*self.dirx
            dist2 = target.dist(self)
            if abs(dist1) < target.height and dist2 > 0 and dist2 < RANGE:
                in_range.append((target,dist1,dist2))
        if not in_range:
            self.fail_sound.play()
            return
        self.lock_sound.play()
        locked = min(in_range,key=thrd)
        self.locked.sprite = locked[0]
        locked[0].lock(locked[2],locked[1] > 0)

    def unlock(self):           # Dying monster are not unlocked...
        pass

    def __call__(self,action):
        self.action[action]()

    def __contains__(self,action):
        return action in self.action

class Monsters(MovingAgent):
    def __init__(self,player):
        MovingAgent.__init__(self, self.containers)

        self.rotatespeed = BOTROTATESPEED

        self.direction = 0
        self.speed = 1
        self._adapt_direction()
        self.locked = False
        self.player = player

    def update(self):
        player = self.player
        if self.locked:
            self.direction = player.direction + self.rotate
            self.move_to(player.posx + player.dirx * self.distance,
                         player.posy + player.diry * self.distance)
            self._adapt_direction()
        else:
            determinant = self.dirx*(self.posy-player.posy)-self.diry*(self.posx-player.posx)
            if determinant > 0:
                self.turn_left()
            else:
                self.turn_right()

            MovingAgent.update(self)

    def lock(self, distance, direct):
        self.locked = True
        self.distance = distance
        if direct:
            self.rotate = 90
        else:
            self.rotate = -90

    def unlock(self):
        self.locked = False

    def kill(self):
        self.die_sound.play()
        MovingAgent.kill(self)
