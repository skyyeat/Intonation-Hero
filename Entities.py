import pygame
from pygame import *
import Constants
import Utils
import Mic

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class PlayerArrow(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)

        self.image = pygame.image.load('Arrow.png')
        self.image.convert()
        self.rect = Rect(x, y, 25, 25)
        self.f0 = Constants.SPEAKER

    def update(self, freq, platforms, CENTER, centerx):

        if freq > 50 and freq < 600:
            self.rect.top = -(Mic.f0dev(freq, self.f0)) + CENTER

        else:
            self.rect.top = CENTER*4


        self.collide(platforms) 

    def collide(self, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if p.hit == 0:
                    self.scene.score()
                    p.image = colorize(p.image, Constants.green)
                    p.hit = 1
        return True

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((25,25))
        self.image.convert()
        self.rect = Rect(x, y, 25, 25)
        self.count = 0
        self.hit = 0

    def update(self, freq, platforms, centery, centerx):
        self.count += 1
        if self.rect.left > 0 and self.count > Constants.SPEED:
                self.count = 0
                self.rect.x -= 1
   
        

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = Surface((25,25)) 
        self.image.convert()
        self.rect = Rect(x, y, 25, 25)
        self.count = 0
        self.hit = 0

    def update(self, freq, platforms, centery, centerx):
        self.count += 1
        if self.rect.left > 0 and self.count > Constants.SPEED:
                self.count = 0
                self.rect.x -= 1



class Transcription(Entity):
    def __init__(self, x, y, transcription):
        Entity.__init__(self)
        self.font = pygame.font.SysFont('timesnewroman', 56)
        w=25
        for c in transcription:
            w+=20
        if transcription[:4] == 'data':
            transcription = ''
        self.rect = Rect(x, y, w, 25)
        self.count = 0
        self.text = self.font.render(transcription, True, (Constants.black))

    def update(self, freq, platforms, centery, centerx):
        self.count += 1
        if self.count>Constants.SPEED:
                self.count = 0
                self.rect.x -= 1


def button(screen,scene, num, msg,x,y,w,h,color,activecolor, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        if click[0] == 1 and action != None:
            activecolor = activecolor
            action(scene, num)

        pygame.draw.rect(screen, activecolor,(x,y,w,h))
    else:
        pygame.draw.rect(screen, color,(x,y,w,h))

    screen.blit(msg, (x, y))

def speedbutton(screen,scene, num, msg,x,y,w,h,color,activecolor, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        #scene.gamespeed = num
        if click[0] == 1 and action != None:
            activecolor = activecolor
            action(scene, num)

        pygame.draw.rect(screen, activecolor,(x,y,w,h))
    else:
        #scene.gamespeed = Constants.SPEED
        pygame.draw.rect(screen, color,(x,y,w,h))

    screen.blit(msg, (x, y))


def playbutton(screen,scene, num, msg,x,y,w,h,color,activecolor, sound):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:

        if click[0] == 1:

            activecolor = Constants.red
            pygame.mixer.Sound.play(sound)
            scene.pause = False
            pygame.time.wait(int(scene.duration)*1200)

        pygame.draw.rect(screen, activecolor,(x,y,w,h))
    else:
        pygame.draw.rect(screen, color,(x,y,w,h))

    screen.blit(msg, (x, y))

#Color Hit
def colorize(image, newColor):
    """
    Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
    original).
    :param image: Surface to create a colorized copy of
    :param newColor: RGB color to use (original alpha values are preserved)
    :return: New colorized Surface instance
    """
    image = image.copy()

    # zero out RGB values
    image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    return image

#Musical Note tones
def note(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(12*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] #+ str(octave)

#Musical Semitone with octave
def semitone(freq):
    A4 = 440
    C0 = A4*pow(2, -4.75)
    name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    h = round(24*log2(freq/C0))
    octave = h // 12
    n = h % 12
    return name[n] + str(octave)

def notepos(note, CENTER):
    WIN_HEIGHT = CENTER*2
    n = WIN_HEIGHT/24
    x = CENTER

    if note == "C":
        x = x - n*1
    elif note == "C#":
        x = x - n*1.5
    elif note == "D":
        x = x - n*2
    elif note == "D#":
        x = x - n*2.5
    elif note == "E":
        x = x - n*3
    elif note == "F":
        x = x + n*3
    elif note == "F#":
        x = x + n*2.5
    elif note == "G":
        x = x + n*2
    elif note == "G#":
        x = x + n*1.5
    elif note == "A":
        x = x + n*1
    elif note == "A#":
        x = x + n*0.5
    elif note == "B":
        x = CENTER

    return x

