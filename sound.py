import pygame
from pygame.locals import *

from const import *
from utils import *

def level_to_x(level):
    return 290 + 50*level


class Selector(pygame.sprite.Sprite):
    def __init__(self,set_volume,level,y):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.font = font.default.render("O", True, (0, 0, 0))
        self.image = pygame.Surface((self.font.get_width()+1,self.font.get_height())).convert()
        self.set_volume = set_volume
        self.level = level
        self.y = y

        self.update()

    def up(self):
        if self.level < 10:
            self.level += 1
            self.set_volume(self.level)

    def down(self):
        if self.level > 0:
            self.level -= 1
            self.set_volume(self.level)

    def update(self,selected = False):
        if selected:
            self.image.fill((200, 200, 200))
        else:
            self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(level_to_x(self.level),self.y))
        rect = self.image.get_rect()
        self.image.blit(self.font,rect)


class Sound():
    def __init__(self, screen):
        background = pygame.Surface(screen.get_size()).convert()
        background.fill((250, 250, 250))
        label = font.default.render("Sound & Music", True, (0, 0, 0))
        rect = label.get_rect(midtop=SCREENRECT.midtop)
        background.blit(label,rect)

        musicy = (SCREENRECT.top + 2*SCREENRECT.centery)/3
        soundy = (SCREENRECT.bottom + 2*SCREENRECT.centery)/3

        labelx = SCREENRECT.left+30

        label = font.default.render("Music", True, (0, 0, 0))
        rect = label.get_rect(midleft=(labelx,musicy))
        background.blit(label,rect)

        label = font.default.render("Sound", True, (0, 0, 0))
        rect = label.get_rect(midleft=(labelx,soundy))
        background.blit(label,rect)

        label = font.default.render(".", True, (0, 0, 0))
        center_music = []
        center_sound = []

        self.selected_entry = pygame.sprite.GroupSingle()
        self.visible = pygame.sprite.RenderUpdates()

        Selector.containers = self.visible

        for i in range(11):
            centerx = level_to_x(i)

            center = (centerx, soundy)
            center_sound.append(center)
            rect = label.get_rect(center=center)
            background.blit(label,rect)

            center = (centerx, musicy)
            center_music.append(center)
            rect = label.get_rect(center=center)
            background.blit(label,rect)

        self.center_music = center_music
        self.musicy = musicy
        self.center_sound = center_sound
        self.soundy = soundy
        self.screen = screen
        self.background = background
        Sound.fail = load_sound('failed.wav')
        Sound.lock = load_sound('success.wav')

        Sound.heroes_die = load_sound('die.wav')

        Sound.monster_die = load_sound('killing.wav')

        Sound.newlevel = load_sound('end-level.wav')
        self.sounds = [ Sound.fail, Sound.lock, Sound.heroes_die, Sound.monster_die, Sound.newlevel]

    def __call__(self):
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        clock = pygame.time.Clock()

        music = self.get_music_volume()
        sound = self.get_sounds_volume()

        self.visible.empty()
        self.selected_entry.empty()

        music_selector = Selector(self.set_music_volume,music,self.musicy)
        sounds_selector = Selector(self.set_sounds_volume,sound,self.soundy)
        self.selected_entry.sprite = music_selector

        def noop(): pass
        def up():
            self.selected_entry.sprite.up()

        def down():
            self.selected_entry.sprite.down()

        def next():
            self.selected_entry.sprite = music_selector

        def prev():
            self.selected_entry.sprite = sounds_selector

        while True:
            nextaction = noop
            for event in pygame.event.get():
                if event.type == QUIT or \
                   (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return
                elif event.type == KEYDOWN and event.key == K_RETURN:
                    return
                elif event.type == KEYDOWN and event.key == K_UP:
                    nextaction = next
                elif event.type == KEYDOWN and event.key == K_DOWN:
                    nextaction = prev
                elif event.type == KEYDOWN and event.key == K_LEFT:
                    nextaction = down
                elif event.type == KEYDOWN and event.key == K_RIGHT:
                    nextaction = up
                elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 1:
                    if event.value > 0.5:
                        nextaction = prev
                    elif event.value < -0.5:
                        nextaction = next
                elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 0:
                    if event.value > 0.5:
                        nextaction = up
                    elif event.value < -0.5:
                        nextaction = down
                elif event.type == JOYBUTTONDOWN and event.joy == 0 and event.button == 0:
                    return
                elif event.type == JOYBUTTONDOWN and event.joy == 0 and (event.button == 2 or event.button == 6):
                    return

            nextaction()

            self.visible.clear(self.screen, self.background)

            self.visible.update()
            self.selected_entry.update(True)

            dirty = self.visible.draw(self.screen)
            pygame.display.update(dirty)

            #cap the framerate
            clock.tick(5)



    def set_sounds_volume(self, volume):
        volume = float(volume)/10
        for sound in self.sounds:
            sound.set_volume(volume)

    def get_sounds_volume(self):
        return int(self.sounds[0].get_volume() * 10)

    def set_music_volume(self,volume):
        volume = float(volume)/10
        pygame.mixer.music.set_volume(volume)

    def get_music_volume(self):
        return int(pygame.mixer.music.get_volume() * 10)
