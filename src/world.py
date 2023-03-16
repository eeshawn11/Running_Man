import pygame
import random

from .config import Config
from . import utils

class World:
    def __init__(self):
        self.background = pygame.image.load("./assets/images/background.jpg").convert()

        self.grass_grp1 = pygame.sprite.Group()
        self.grass_grp2 = pygame.sprite.Group()
        self.lamp_posts = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()

        for i in range(62):
            tile = Tile()
            tile.rect.x = i * tile.width
            tile.rect.y = Config.GROUND_HEIGHT
            self.ground.add(tile)
        
        for i in range(21):
            grass = Grass()
            flip_x = random.randint(0, 1)
            grass.image = pygame.transform.flip(grass.image, flip_x, False)
            grass.rect.x = (i * grass.width) - random.randint(0, 20)
            grass.rect.bottom = Config.GROUND_HEIGHT + random.randint(0, 2)
            self.grass_grp1.add(grass)

        for i in range(18):
            grass = Grass()
            flip_x = random.randint(0, 1)
            grass.image = pygame.transform.flip(grass.image, flip_x, False)
            grass.rect.x = (i * grass.width) - random.randint(0, 20)
            grass.rect.bottom = Config.GROUND_HEIGHT + random.randint(3, 6)
            self.grass_grp2.add(grass)
        
        for i in range(2):
            lamp = Lamp()
            distance_btw_lamps = Config.S_WIDTH // 2
            lamp.rect.x = i * distance_btw_lamps
            lamp.rect.bottom = Config.GROUND_HEIGHT
            self.lamp_posts.add(lamp)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))

        self.grass_grp1.update()
        self.grass_grp1.draw(screen)

        self.lamp_posts.update()
        self.lamp_posts.draw(screen)
        
        self.grass_grp2.update()
        self.grass_grp2.draw(screen)

        self.ground.update()
        self.ground.draw(screen)

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image_path, alpha=False):
        super().__init__()
        self.image = pygame.image.load(image_path)
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.width = self.rect.width

    def update(self):
        self.rect.x += Config.SCROLL
        if self.rect.right < 0:
            self.rect.x = Config.S_WIDTH

class Tile(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/tile_ground.png")

class Grass(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/decor_grass.png", alpha=True)

class Lamp(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/lamp.png", alpha=True)