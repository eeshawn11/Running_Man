import pygame
from .config import Config

pygame.mixer.init()

class Audio():
    def __init__(self):
        self.__jump_fx = pygame.mixer.Sound("./assets/audio/jump.mp3")
        self.__jump_fx.set_volume(Config.VOLUME)
        self.__hit_fx = pygame.mixer.Sound("./assets/audio/hit.wav")
        self.__hit_fx.set_volume(Config.VOLUME)
        self.__point_fx = pygame.mixer.Sound("./assets/audio/point.wav")
        self.__point_fx.set_volume(Config.VOLUME)

    def start_bgm(self):
        pygame.mixer.music.load("./assets/audio/8bit_bgm.mp3")
        pygame.mixer.music.set_volume(Config.VOLUME)
        pygame.mixer.music.play(loops=-1)

    def fade_bgm(self, time: int=3):
        time *= 1000
        pygame.mixer.music.fadeout(time)

    def jump(self):
        self.__jump_fx.play()

    def hit(self):
        self.__hit_fx.play()

    def point(self):
        self.__point_fx.play()