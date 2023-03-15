import pygame
import random
from .config import Config

vec = pygame.math.Vector2

class Obstacle(pygame.sprite.Sprite):
    colors = ["black", "gray", "dark gray"]

    def __init__(self, width=random.randint(30,70), height=random.randint(30,70)):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(random.choice(Obstacle.colors))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = vec((Config.S_WIDTH+self.rect.width, Config.GROUND_HEIGHT-self.rect.height))
        self.speed = -random.randint(5,10)
        self.rect.topleft = self.start_pos
        self.hit = True

    def update(self):
        dx = 0
        dx += self.speed
        self.rect.x += dx
    
    def reset(self):
        self.rect.topleft = self.start_pos
        self.hit = True
        self.speed = -random.randint(5,10)