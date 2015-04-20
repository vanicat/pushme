import pygame
from actors import Heroes, Monsters
from scoring import Scoring
from const import *

from pygame.locals import *
from utils import *
import math

class Game():
    def __init__(self,screen):
        self.screen = screen
        # Set background
        self.background = pygame.Surface(screen.get_size()).convert()

        self.background_filling()


        # Groups of sprite
        self.monsters = pygame.sprite.Group()
        self.breakable = pygame.sprite.Group()
        self.visible = pygame.sprite.RenderUpdates()

        Heroes.containers = self.visible, self.breakable
        Monsters.containers = self.visible, self.monsters, self.breakable
        Scoring.containers = self.visible

        # images
        Heroes.src_image = load_image('heroes.png')
        Monsters.src_image = load_image('monsters.png')

        # sounds
        Heroes.fail_sound = load_sound('failed.wav')
        Heroes.lock_sound = load_sound('success.wav')

        Heroes.die_sound = load_sound('die.wav')

        Monsters.die_sound = load_sound('killing.wav')
        Monsters.wall_sound = load_sound('wall.wav')

        self.newlevel_sound = load_sound('end-level.wav')
        self.clock = pygame.time.Clock()

    def __call__(self):
        self.monsters.empty()
        self.breakable.empty()
        self.visible.empty()

        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        # The actors
        self.player = Heroes(self.monsters)
        self.nummonster = 0
        score = Scoring()

        # a clock

        self.action = {
            K_RIGHT: self.player.turn_right,
            K_LEFT: self.player.turn_left,
            K_DOWN: self.player.brake,
            K_UP: self.player.accelerate,
            K_SPACE: self.player.lock,
        }

        self.stoping = {
            K_RIGHT: self.player.no_turn,
            K_LEFT: self.player.no_turn,
            K_DOWN: self.player.no_accel,
            K_UP: self.player.no_accel,
            K_SPACE: self.player.unlock,
        }

        self.paused = False

        while self.player.alive():
            if self.get_input():
                return score.score

            if not self.monsters.sprites():
                self.level_up()

            # clear/erase the last drawn sprites
            self.visible.clear(self.screen, self.background)

            #update visible the sprites
            if not self.paused: self.visible.update()

            if not SCREENRECT.contains(self.player.rect):
                self.player.kill()

            compare_to = []
            broken = set([])
            for sprite in self.monsters:
                if sprite.dist(self.player) < (self.player.width + sprite.width - 4 )/2:
                    self.player.kill()
                elif sprite not in broken:
                    if not SCREENRECT.contains(sprite.rect) and sprite.locked:
                        r = sprite.width/2
                        if sprite.posx - r < SCREENRECT.left:
                            sprite.posx = SCREENRECT.left + r
                        elif sprite.posx + r > SCREENRECT.right:
                            sprite.posx = SCREENRECT.right - r
                        if sprite.posy - r < SCREENRECT.top:
                            sprite.posy = SCREENRECT.top + r
                        elif sprite.posy + r > SCREENRECT.bottom:
                            sprite.posy = SCREENRECT.bottom - r
                        sprite.distance = sprite.dist(self.player)

                    for other in compare_to:
                        if sprite.dist(other) < sprite.width - 3:
                            score.collide(sprite,other)
                            broken.add(sprite)
                            broken.add(other)
                            break

                    compare_to.append(sprite)

            for sprite in broken:
                sprite.kill()

            #draw the scene
            dirty = self.visible.draw(self.screen)
            pygame.display.update(dirty)

            #cap the framerate
            self.clock.tick(60)

        end_sound(self.clock)

        return score.score

    def background_filling(self):
        self.background.fill((62,120,112))
        imgbg = load_image('background-tile.png')
        rect = imgbg.get_rect()
        height=rect.height
        width=rect.width
        rect.move_ip((-10,-32))
        for i in range(13):
            for j in range(8):
                self.background.blit(imgbg,rect.move((i*(width+3),j*(height+54))))
                self.background.blit(imgbg,rect.move((i*(width+3)-width/2-2,j*(height+54)+77)))


    #
    # reading the input
    #
    def get_input(self):
        #get input
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key in self.action:
                self.action[event.key]()
            elif event.type == KEYUP and event.key in self.stoping:
                self.stoping[event.key]()
            elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 0:
                self.player.turn(event.value)
            elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 1:
                self.player.accel(-event.value)
            elif event.type == JOYBUTTONDOWN and event.joy == 0 and event.button == 0:
                self.player.lock()
            elif event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return True
            elif event.type == KEYDOWN and event.key == K_RETURN:
                self.paused = not self.paused

    #
    # level_up: call this when everybody is dead
    #
    def level_up(self):
        end_sound(self.clock)
        self.newlevel_sound.play()
        self.player.center()
        self.nummonster += 2
        angle = 2*math.pi/self.nummonster
        for i in range(self.nummonster):
            Monsters(self.player).move_to(SCREENRECT.centerx+SIZE*math.cos(angle*i),
                                          SCREENRECT.centery+SIZE*math.sin(angle*i))
