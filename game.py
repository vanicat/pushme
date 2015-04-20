import pygame
from actors import Heroes, Monsters
from scoring import Scoring
from const import *

from pygame.locals import *
from utils import *
import math

class Game():
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

    def __call__(self):
        self.monsters.empty()
        self.breakable.empty()
        self.visible.empty()

        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        # The actors
        player = Heroes(self.monsters)
        nummonster = 0
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
                    return score.score
                elif event.type == KEYDOWN and event.key == K_RETURN:
                    paused = not paused


            if not self.monsters.sprites():
                end_sound(clock)
                self.newlevel_sound.play()
                player.center()
                nummonster += 2
                angle = 2*math.pi/nummonster
                for i in range(nummonster):
                    Monsters(player).move_to(SCREENRECT.centerx+SIZE*math.cos(angle*i),
                                             SCREENRECT.centery+SIZE*math.sin(angle*i))

            # clear/erase the last drawn sprites
            self.visible.clear(self.screen, self.background)

            #update visible the sprites
            if not paused: self.visible.update()

            if not SCREENRECT.contains(player.rect):
                player.kill()

            compare_to = []
            broken = set([])
            for sprite in self.monsters:
                if sprite.dist(player) < (player.width + sprite.width - 4 )/2:
                    player.kill()
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
                        sprite.distance = sprite.dist(player)

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
            clock.tick(60)

        end_sound(clock)

        return score.score
