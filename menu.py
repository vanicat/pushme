import pygame
from pygame.locals import *

import const

class LineC():
    def lf(self):
        Line.pos += const.LINEHEIGHT

    def menu_lf(self):
        Line.pos += const.MENUHEIGHT

    def output(self, text, color, font, lf):
        label = font.render(text, True, color)
        text_rect = label.get_rect(midtop=const.SCREENRECT.midtop)
        text_rect.move_ip(0,Line.pos)
        self.screen.blit(label,text_rect)
        lf()


    def big(self, text, color = (0,0,0,255)):
        self.output(text, color, const.font.other, self.menu_lf)

    def small(self, text, color = (0,0,0,255)):
        self.output(text, color, const.font.small, self.lf)


Line = LineC()


class MenuEntry(pygame.sprite.Sprite):
    def __init__(self,label,result,width):
        pygame.sprite.Sprite.__init__(self,self.containers)

        self.image = pygame.Surface((width,const.MENUHEIGHT),flags=SRCALPHA).convert_alpha()
        self.image.fill((255, 255, 255, 0))

        self.rect = self.image.get_rect(midtop=const.SCREENRECT.midtop)


        self.label = const.font.menu.render(label, True, (0,0,0,255))
        self.label_rect = self.label.get_rect(center=self.rect.center)

        self.rect.move_ip(0,Line.pos)

        Line.menu_lf()

        self.result   = result

        self.prev = MenuEntry.prev
        MenuEntry.prev = self
        if self.prev:
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
    MenuEntry.prev = None
    Line.pos = 0
    Line.screen = screen

    Line.lf()
    Line.big("Move Them",color = (22,22,90))
    Line.small("You are alone")
    Line.small("They want you")
    Line.small("And this is not a cannon you have")
    Line.lf()
    Line.lf()
    Line.lf()
    Line.small("Use arrow key to control, space to lock")
    Line.small("or a pad (A to lock)")
    Line.lf()

    pygame.display.flip()

    selected_entry.add(MenuEntry("Play",'play',screen.get_width()))
    MenuEntry("Sound and Music",'sound',screen.get_width())
    MenuEntry("Highscore",'score',screen.get_width())
    MenuEntry("Quit",'quit',screen.get_width())

    # a clock
    clock = pygame.time.Clock()

    def noop(): pass
    def next():
        if selected_entry.sprite.next:
            selected_entry.add(selected_entry.sprite.next)
    def prev():
        if selected_entry.sprite.prev:
            selected_entry.add(selected_entry.sprite.prev)


    while True:
        nextaction = noop
        for event in pygame.event.get():
            if event.type == QUIT or \
                (event.type == KEYDOWN and event.key == K_ESCAPE):
                return 'quit'
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return selected_entry.sprite.result
            elif event.type == KEYDOWN and event.key == K_UP:
                nextaction = prev
            elif event.type == KEYDOWN and event.key == K_DOWN:
                nextaction = next
            elif event.type == JOYAXISMOTION and event.joy == 0 and event.axis == 1:
                if event.value > 0.5:
                    nextaction = next
                elif event.value < -0.5:
                    nextaction = prev
            elif event.type == JOYBUTTONDOWN and event.joy == 0 and event.button == 0:
                return selected_entry.sprite.result
            elif event.type == JOYBUTTONDOWN and event.joy == 0 and (event.button == 2 or event.button == 6):
                return 'quit'

        nextaction()

        visible.clear(screen, background)

        visible.update(False)

        selected_entry.update(True)

        dirty = visible.draw(screen)
        pygame.display.update(dirty)

        #cap the framerate
        clock.tick(5)
