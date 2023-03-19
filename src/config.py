from pygame.locals import *
from enum import Enum

class GameState(Enum):
    GAME_PLAY = 0
    GAME_PAUSE = 1
    GAME_END = 2

class Config:
    """Global game settings, configure as required."""
    # frame rate
    FPS = 30
    # screen dimensions
    S_WIDTH = 960 
    S_HEIGHT = 540
    # easy collision check
    GROUND_HEIGHT = S_HEIGHT - 16
    # world effects
    GRAVITY = 1.5
    FRICTION = 1
    # audio volume
    volume = 0.1
    # background scroll speed
    scroll = -2
    # game status
    status = GameState.GAME_PLAY

    # key bindings
    left_keybind = [K_a]
    right_keybind = [K_d]
    up_keybind = [K_w]
    pause_keybind = [K_e]
    exit_keybind = [K_q]