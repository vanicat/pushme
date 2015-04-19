#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want with this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
from pygame.locals import *
import os.path, math

from const import *
import const
from actors import *
from scoring import *
import menu

def load_image(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as error:
        print("Impossible de charger l'image : {0}", error)
        raise SystemExit, message
    image = image.convert_alpha()
    return image

def game(screen):
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
                        if sprite.dist(other) < sprite.width:
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
    return score.score




def main():
    pygame.init()

    const.font_init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    todo = menu.menu(screen)
    while todo != 'quit':
        game(screen)
        todo = menu.menu(screen)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()
