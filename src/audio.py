import pygame
from .config import Config

pygame.mixer.init()

class Audio():
    def __init__(self):
        self.jump_fx = pygame.mixer.Sound("./assets/audio/jump.mp3")
        self.jump_fx.set_volume(Config.VOLUME)

    def start_bgm(self):
        pygame.mixer.music.load("./assets/audio/8bit_bgm.mp3")
        pygame.mixer.music.set_volume(Config.VOLUME)
        pygame.mixer.music.play(loops=-1)

    def jump(self):
        self.jump_fx.play()