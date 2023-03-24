import pygame
import random
import json
import logging

from .config import Config

class Background():
    def __init__(self, x, y):
        self.images = []
        self.rects = []

        for img in range(5):
            bg_image = pygame.image.load(f"./assets/images/background_layer_{img}.png").convert_alpha()
            bg_image = pygame.transform.scale_by(bg_image, 2.5)
            bg_rect = bg_image.get_rect()
            bg_rect.topleft = (x, y)

            self.images.append(bg_image)
            self.rects.append(bg_rect)

    def update(self):
        for rect in self.rects:
            rect.x += Config.BG_SCROLL
            if rect.right <= 0:
                rect.x = Config.S_WIDTH

    def draw(self, screen):
        screen.blits(blit_sequence=zip(self.images, self.rects))


class SpriteObject(pygame.sprite.Sprite):
    def __init__(self, image_path: str, alpha: bool=False, flip: bool=False, scale : float=1.0):
        super().__init__()
        self.logger = logging.getLogger("runningman.visuals.SpriteObject")
        self.image = pygame.image.load(image_path)
        if alpha:
            self.image = self.image.convert_alpha()
        else:
            self.image = self.image.convert()
        if flip:
            self.image = self.flip_x(self.image)
        if scale:
            self.image = pygame.transform.scale_by(self.image, scale)
        self.width = self.image.get_width()
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.x += Config.scroll
        if self.rect.right <= 0:
            self.rect.x = Config.S_WIDTH

    @staticmethod
    def flip_x(image: pygame.Surface) -> pygame.Surface:
        """Randomly flips and returns a PyGame Surface"""
        flip_x = random.randint(0, 1)
        image = pygame.transform.flip(image, flip_x, False)
        return image

class Tile(SpriteObject):
    def __init__(self):
        super().__init__("./assets/images/tile_ground.png")
        self.prev = None

    def get_right(self):
        return self.rect.right

    def update(self):
        """Using a linked list, reassign tile to the end of the list."""
        self.rect.x += Config.scroll
        if self.rect.right <= 0:
            if self.prev is None:
                self.rect.x = Config.S_WIDTH
            else:
                self.rect.x = self.prev.get_right()

class Grass(SpriteObject):
    count = 4
    paths = [f"./assets/images/grass{i}.png" for i in range(count)]

    def __init__(self):
        path = random.choice(Grass.paths)
        super().__init__(path, alpha=True, flip=True)

class Bush(SpriteObject):
    count = 3
    paths = [f"./assets/images/bush{i}.png" for i in range(count)]

    def __init__(self):
        path = random.choice(Bush.paths)
        super().__init__(path, alpha=True, flip=True, scale=random.uniform(0.5, 1.0))

class Tree(SpriteObject):
    count = 2
    paths = [f"./assets/images/tree{i}.png" for i in range(count)]

    def __init__(self):
        path = random.choice(Tree.paths)
        super().__init__(path, alpha=True, flip=True, scale=random.uniform(1.5, 2.5))

    def update(self):
        self.rect.x += Config.scroll
        if self.rect.right <= 0:
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