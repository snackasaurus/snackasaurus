#!/usr/bin/python

import pygame, os

pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('song.wav')
pygame.mixer.music.play(-1)


# dircur = os.path.dirname(__file__)
# filename = os.path.join(dircur, 'song.ogg')
# pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
# song = pygame.mixer.Sound(filename)
# pygame.mixer.Sound.play(song)

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# while(1):
#     s = Sound()
#     s.read('song.mp3')
#     s.play()
