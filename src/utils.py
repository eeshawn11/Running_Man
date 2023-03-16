import pygame
import random
from .config import Config

def load_and_scale_image(filename: str, alpha: bool=False) -> pygame.Surface:
    """Load and convert PyGame image."""
    if alpha:
        image = pygame.image.load(filename).convert_alpha()
    elif not alpha:
        image = pygame.image.load(filename).convert()
    image = pygame.transform.scale2x(image)
    return image

def apply_friction(velocity: float) -> float:
    """Calculate and return velocity after applying friction."""
    if velocity > 0:
        velocity -= Config.FRICTION
        if velocity - Config.FRICTION < 0:
            velocity = 0
    elif velocity < 0:
        velocity += Config.FRICTION
        if velocity + Config.FRICTION > 0:
            velocity = 0
    return velocity

def flip_x(image: pygame.Surface) -> pygame.Surface:
    """Randomly flips and returns a PyGame Surface"""
    flip_x = random.randint(0, 1)
    image = pygame.transform.flip(image, flip_x, False)
    return image