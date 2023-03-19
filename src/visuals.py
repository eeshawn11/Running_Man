import pygame
import random
import json
import logging

log = logging.getLogger("runningman.visuals")

from .config import Config

def load_background() -> pygame.Surface:
    return pygame.image.load("./assets/images/background.jpg").convert()

def flip_x(image: pygame.Surface) -> pygame.Surface:
    """Randomly flips and returns a PyGame Surface"""
    flip_x = random.randint(0, 1)
    image = pygame.transform.flip(image, flip_x, False)
    return image

class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image_path: str, alpha: bool=False, flip: bool=False):
        super().__init__()
        self.image = pygame.image.load(image_path)
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()
        if flip:
            self.image = flip_x(self.image)
        self.width = self.image.get_width()
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += Config.scroll
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
        self.rect.x += Config.scroll
        if self.rect.right < 0:
            self.kill()

class Heart(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/heart.png", alpha=True)
        self.image = pygame.transform.scale2x(self.image)
    
class PlayerSprites:
    # update to load and store sprites in cache
    def __init__(self, filename: str="./assets/adventurer/simple_adventurer.png"):
        self.sprite_sheet = pygame.image.load(filename).convert()
        with open(filename.replace("png", "json")) as f:
            self.metadata = json.load(f)
        self.actions = self.metadata.keys()

    def num_frames(self, action: str):
        return self.metadata[action]["frames"]

    def get_sprite(self, x: int, y: int, w: int, h: int):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        sprite = pygame.transform.scale2x(sprite)
        return sprite

    def parse_sprite(self, action: str, frame: int):
        sprites = self.metadata[action]["sprites"]
        if frame >= self.num_frames(action):
            frame = self.num_frames(action) - 1
        x, y, w, h = sprites[frame].values()
        image = self.get_sprite(x, y, w, h)
        return image