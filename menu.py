import pygame
from pygame.locals import *

import const

class MenuEntry(pygame.sprite.Sprite):
    def __init__(self,label,result,width,posy,prev = None):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.image = pygame.Surface((width,const.MENUHEIGHT),flags=SRCALPHA).convert_alpha()
        self.image.fill((255, 255, 255, 0))

        self.rect = self.image.get_rect(midtop=const.SCREENRECT.midtop)


        self.label = const.font.menu.render(label, True, (0,0,0,255))
        self.label_rect = self.label.get_rect(center=self.rect.center)

        self.rect.move_ip(0,posy)

        self.result   = result

        self.prev = prev
        if prev:
            self.prev.next = self
        self.next = None

    def update(self,selected):
        if selected:
            alpha = 125
        else:
            alpha = 0
        self.image.fill((0, 0, 0, alpha))
        self.image.blit(self.label, self.label_rect)



def menu(screen):
    background = pygame.Surface(screen.get_size()).convert()
    # imgbg = load_image('background-menu.png')
    background.fill((250, 250, 250))
    #background.blit(imgbg,(0,0))
    screen.blit(background, (0,0))
    pygame.display.flip()

    # Groups of sprite
    entries = pygame.sprite.Group()
    selected_entry = pygame.sprite.GroupSingle()
    visible = pygame.sprite.RenderUpdates()

    MenuEntry.containers = visible, entries

    menu = MenuEntry("Play",'play',screen.get_width(),0)
    selected_entry.add(menu)
    menu = MenuEntry("Quit",'quit',screen.get_width(),const.MENUHEIGHT,prev=menu)

    # a clock
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                return 'quit'
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return selected_entry.sprite.result
            elif event.type == KEYDOWN and event.key == K_UP and selected_entry.sprite.prev:
                selected_entry.add(selected_entry.sprite.prev)
            elif event.type == KEYDOWN and event.key == K_DOWN and selected_entry.sprite.next:
                selected_entry.add(selected_entry.sprite.next)

        visible.clear(screen, background)

        visible.update(False)

        selected_entry.update(True)

        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(60)
