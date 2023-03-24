import pygame
import random
from .config import Config

vec = pygame.math.Vector2

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, image_path: str, scale: float=1.0):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        if scale:
            self.image = pygame.transform.scale_by(self.image, scale)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.start_pos = vec((Config.S_WIDTH, Config.GROUND_HEIGHT))
        self.rect.bottomleft = self.start_pos

    def update(self):
        self.rect.x += Config.scroll
    
    def check_score(self):
        if self.rect.right < 0:
            self.kill()
            return True
        return False

    @staticmethod
    def gen():
        choice = random.randint(0, 99)
        if choice < 5:
            return Statue()
        elif choice < 10:
            return Signboard()
        elif choice < 30:
            return Scarecrow()
        elif choice < 80:
            return random.choice([Crate(), Box()])
        else:
            return Logs()

class Logs(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/logs.png", 1.5)

class Crate(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/crate.png")

class Box(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/box.png")

class Signboard(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/signboard.png", 1.5)

class Scarecrow(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/scarecrow.png", 1.2)

class Statue(Obstacle):
    def __init__(self):
        super().__init__("./assets/images/statue.png", 1.5)