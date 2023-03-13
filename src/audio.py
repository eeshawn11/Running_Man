import pygame
from .config import Config

pygame.mixer.init()

class Audio():
    def __init__(self):
        self.jump_fx = pygame.mixer.Sound("./assets/audio/jump.mp3")
        self.jump_fx.set_volume(Config.VOLUME)