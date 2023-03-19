import pygame
from .config import Config

class AudioService():
    @staticmethod
    def start_bgm():
        pygame.mixer.music.load("./assets/audio/8bit_bgm.mp3")
        pygame.mixer.music.set_volume(Config.volume)
        pygame.mixer.music.play(loops=-1)

    @staticmethod
    def fade_bgm(time: int=3):
        time *= 1000
        pygame.mixer.music.fadeout(time)

    @staticmethod
    def pause_bgm():
        pygame.mixer.music.pause()
    
    @staticmethod
    def resume_bgm():
        pygame.mixer.music.unpause()

    @staticmethod
    def jump():
        jump_fx = pygame.mixer.Sound("./assets/audio/jump.mp3")
        jump_fx.set_volume(Config.volume)
        jump_fx.play()

    @staticmethod
    def hit():
        hit_fx = pygame.mixer.Sound("./assets/audio/hit.wav")
        hit_fx.set_volume(Config.volume)
        hit_fx.play()

    @staticmethod
    def score():
        score_fx = pygame.mixer.Sound("./assets/audio/score.wav")
        score_fx.set_volume(Config.volume)
        score_fx.play()