import pygame
import random

from .config import Config

class World:
    def __init__(self):
        self.background = pygame.image.load("./assets/images/background.jpg").convert()
        self.tile = pygame.image.load("./assets/images/tile_ground.png").convert()
        self.objects = {
            0: pygame.image.load("./assets/images/decor_grass.png").convert_alpha(),
            1: pygame.image.load("./assets/images/decor_rock.png").convert_alpha(),
            2: pygame.image.load("./assets/images/decor_large_rock.png").convert_alpha(),
        }
        self.ground = []
        self.decor = []

        for i in range(Config.S_WIDTH//self.tile.get_width()):
            self.ground.append((self.tile, (i*self.tile.get_width(), Config.GROUND_HEIGHT)))
            # add random decor
            choice = random.randint(0,10)
            if choice <= 2:
                self.decor.append((self.objects[choice], (i*self.tile.get_width(), Config.GROUND_HEIGHT-self.objects[choice].get_height())))

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blits(self.ground)
        screen.blits(self.decor)