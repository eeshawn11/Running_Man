import pygame
import random

from .config import Config
from . import utils

class World:
    def __init__(self):
        self.background = pygame.image.load("./assets/images/background.jpg").convert()

        self.rear_grass = pygame.sprite.Group()
        self.fore_grass = pygame.sprite.Group()
        self.lamp_posts = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()

        for i in range(62):
            tile = Tile()
            tile.rect.x = i * tile.width
            tile.rect.y = Config.GROUND_HEIGHT
            self.ground.add(tile)
        
        for i in range(21):
            grass = Grass()
            grass.rect.x = (i * grass.width) - random.randint(0, 20)
            grass.rect.bottom = Config.GROUND_HEIGHT + random.randint(0, 2)
            self.rear_grass.add(grass)

        for i in range(17):
            grass = Grass()
            grass.rect.x = (i * grass.width) - random.randint(0, 20)
            grass.rect.bottom = Config.GROUND_HEIGHT + random.randint(3, 6)
            self.fore_grass.add(grass)
        
        lamps = 2
        for i in range(lamps):
            lamp = Lamp()
            distance_btw_lamps = Config.S_WIDTH // lamps
            lamp.rect.x = i * distance_btw_lamps
            lamp.rect.bottom = Config.GROUND_HEIGHT
            self.lamp_posts.add(lamp)

        tree = Tree()
        tree.rect.centerx = random.choice([350, 400, 450])
        tree.rect.bottom = Config.GROUND_HEIGHT
        self.trees.add(tree)
        self.last_tree = tree


    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))

        self.rear_grass.update()
        self.rear_grass.draw(screen)

        self.trees.update()
        if Config.S_WIDTH - self.last_tree.rect.right > random.choice([450, 500, 550]):
            new_tree = Tree()
            new_tree.rect.x = Config.S_WIDTH
            new_tree.rect.bottom = Config.GROUND_HEIGHT
            self.last_tree = new_tree
            self.trees.add(new_tree)
        self.trees.draw(screen)

        self.lamp_posts.update()
        self.lamp_posts.draw(screen)
        
        self.fore_grass.update()
        self.fore_grass.draw(screen)

        self.ground.update()
        self.ground.draw(screen)

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image_path, alpha=False, flip=False):
        super().__init__()
        self.image = pygame.image.load(image_path)
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()
        if flip:
            self.image = utils.flip_x(self.image)
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
        super().__init__("./assets/images/decor_grass.png", alpha=True, flip=True)

class Lamp(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/lamp.png", alpha=True)

class Tree(SpriteObject):
    paths = [f"./assets/images/tree{i}.png" for i in range(2)]

    def __init__(self):
        path = random.choice(Tree.paths)
        super().__init__(path, alpha=True, flip=True)

    def update(self):
        self.rect.x += Config.SCROLL
        if self.rect.right < 0:
            self.kill()