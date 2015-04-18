#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want with this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
from pygame.locals import *
import os.path, math

SIZE           = 300
SCREENRECT     = Rect(0, 0, 1000, 700)
PLROTATESPEED  = 2
BOTROTATESPEED = 1
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
        self.image=self.font.render("Score: {}".format(self.score),True, (0,0,0,255))
        self.rect = self.image.get_rect(midtop=SCREENRECT.midtop)



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

        self.locked = None

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


    def lock(self):
        def thrd(x):
            x[2]

        in_range = []
        for target in self.targets:
            dist1 = (target.posx-self.posx)*self.diry - (target.posy-self.posy)*self.dirx
            dist2 = target.dist(self)
            if abs(dist1) < target.height and dist2 > 0 and dist2 < RANGE:
                in_range.append((target,dist1,dist2))
        if not in_range: return
        locked = min(in_range,key=thrd)
        self.locked = locked[0]
        locked[0].lock(locked[2],locked[1] > 0)

    def unlock(self):           # Dying monster are not unlocked...
        if self.locked:
            self.locked.unlock()
            self.locked = None


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
        pass

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
    breakable = pygame.sprite.Group()
    visible = pygame.sprite.RenderUpdates()

    Heroes.containers = visible, breakable
    Monsters.containers = visible, monsters, breakable
    Scoring.containers = visible

    # images
    Heroes.src_image = load_image('heroes.png')
    Monsters.src_image = load_image('monsters.png')

    # fonts
    Scoring.font = pygame.font.Font("data/Comfortaa-Light.ttf",20)


    # The actors
    player = Heroes(monsters)
    nummonster = 1
    score = Scoring()

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

    paused = False

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if joysticks:
        joystick=joysticks[0]
        joystick.init()

    while player.alive():
        #get input
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key in action:
                action[event.key]()
            elif event.type == KEYUP and event.key in stoping:
                stoping[event.key]()
            elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 0:
                player.turn(event.value)
            elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 1:
                player.accel(-event.value)
            elif event.type == JOYBUTTONDOWN and event.joy == 0 and event.button == 0:
                player.lock()
            elif event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
            elif event.type == KEYDOWN and event.key == K_RETURN:
                paused = not paused


        if not monsters.sprites():
            player.center()
            nummonster += 1
            angle = 2*math.pi/nummonster
            for i in range(nummonster):
                Monsters(player).move_to(SCREENRECT.centerx+SIZE*math.cos(angle*i),
                                         SCREENRECT.centery+SIZE*math.sin(angle*i))

        # clear/erase the last drawn sprites
        visible.clear(screen, background)

        #update visible the sprites
        if not paused: visible.update()

        if not SCREENRECT.contains(player.rect):
            player.kill()

        compare_to = []
        broken = set([])
        for sprite in monsters:
            if sprite.dist(player) < (player.width + sprite.width)/2:
                player.kill()
            else:
                if not SCREENRECT.contains(sprite.rect) and sprite.locked:
                    broken.add(sprite)
                    score.wall(sprite)
                else:
                    for other in compare_to:
                        if sprite.dist(other) < (other.width + sprite.width)/2:
                            score.collide(sprite,other)
                            broken.add(sprite)
                            broken.add(other)

                compare_to.append(sprite)

        for sprite in broken:
            sprite.kill()

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
