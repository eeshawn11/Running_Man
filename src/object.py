import pygame
import random
from .config import Config

vec = pygame.math.Vector2

class Obstacle(pygame.sprite.Sprite):
    colors = ["black", "gray", "dark gray"]

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([random.randint(30,70), random.randint(30,70)])
        self.image.fill(random.choice(Obstacle.colors))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = vec((Config.WIDTH+10, Config.HEIGHT-self.rect.height-5))
        self.speed = -random.randint(5,10)
        self.rect.topleft = self.start_pos
        self.hit = True

    def move(self):
        dx = 0
        dx += self.speed
        self.rect.x += dx
    
    def reset(self):
        self.rect.topleft = self.start_pos

    def draw(self, screen: pygame.Surface, box: bool=False):
        screen.blit(self.image, self.rect)
        if box:
            pygame.draw.rect(screen, "white", self.rect, 1)