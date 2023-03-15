import pygame
from .config import Config

def load_and_scale_image(filename: str, alpha: bool=False) -> pygame.Surface:
    """Load and convert pygame image."""
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