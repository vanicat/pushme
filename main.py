#! /bin/env python2
# Copyright Remi Vanicat <vanicat@debian.org>
# Licence under CC0: do what ever you want with this
# https://creativecommons.org/publicdomain/zero/1.0/

import pygame
try:
    import pygame._view
except ImportError:
    pass
from pygame.locals import *
import os.path, math

from const import *
import const
from actors import *
from scoring import *
import menu
import highscore

def load_image(name):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as error:
        print("Impossible de charger l'image : {0}", error)
        raise SystemExit, message
    image = image.convert_alpha()
    return image

class dummysound:
    def play(self): pass

def load_sound(file):
    if not pygame.mixer: return dummysound()
    file = os.path.join('data', file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print ('Warning, unable to load, %s' % file)
    return dummysound()

def end_sound(clock):
    while pygame.mixer.get_busy():
        clock.tick(60)

def background_filling(background):
    background.fill((62,120,112))
    imgbg = load_image('background-tile.png')
    rect = imgbg.get_rect()
    height=rect.height
    width=rect.width
    rect.move_ip((-10,-32))
    for i in range(13):
        for j in range(8):
            background.blit(imgbg,rect.move((i*(width+3),j*(height+54))))
            background.blit(imgbg,rect.move((i*(width+3)-width/2-2,j*(height+54)+77)))



def game(screen):
    # Set background
    background = pygame.Surface(screen.get_size()).convert()

    background_filling(background)

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

    # sounds
    Heroes.fail_sound = load_sound('failed.wav')
    Heroes.lock_sound = load_sound('success.wav')

    Heroes.die_sound = load_sound('die.wav')

    Monsters.die_sound = load_sound('killing.wav')
    Monsters.wall_sound = load_sound('wall.wav')

    newlevel_sound = load_sound('end-level.wav')

    # The actors
    player = Heroes(monsters)
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


        if not monsters.sprites():
            end_sound(clock)
            newlevel_sound.play()
            player.center()
            nummonster += 2
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
        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(60)

    end_sound(clock)

    return score.score


def main():
    pygame.init()

    if pygame.mixer and not pygame.mixer.get_init():
        print ('Warning, no sound')
        pygame.mixer = None

    pygame.mixer.music.load('data/tchtada.ogg')
    pygame.mixer.music.play(-1)

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    if joysticks:
        joystick=joysticks[0]
        joystick.init()


    const.font_init()
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    todo = menu.menu(screen)
    while todo != 'quit':
        if todo == 'play':
            score = game(screen)
            highscore.call(screen,score)
        elif todo == 'score':
            highscore.call(screen,None)
        todo = menu.menu(screen)

    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    pygame.quit()



#call the "main" function if running this script
if __name__ == '__main__': main()
