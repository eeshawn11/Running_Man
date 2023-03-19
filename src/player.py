import pygame
import logging

log = logging.getLogger("runningman.player")

from .config import Config
from .audio_service import AudioService
from .visuals import PlayerSprites

vec = pygame.math.Vector2

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

class Player(pygame.sprite.Sprite):
    def __init__(self, health: int=5):
        super().__init__()
        self.logger = logging.getLogger("runningman.player.Player")
        self._speed = 6
        self.hp = health
        self.start_pos = (75, Config.GROUND_HEIGHT)

        # player status
        self.immunity = 0
        self._action = "walk"
        self.velocity = vec(0, 0)
        self.move_left = False
        self.move_right = False
        self.jump = False
        self.in_air = False

        # player sprite
        self.sprites = PlayerSprites()
        self.animation_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_animation()
        self.rect = self.image.get_rect(bottomleft=self.start_pos)
        self.logger.info("Player object initialised")

    def get_status(self):
        if self.hp > 0:
            if self.jump or self.in_air:
                self.update_action("jump")
            elif self.move_left or self.move_right:
                self.update_action("run")
            else:
                self.update_action("walk")

    def update_action(self, new_action: str):
        if new_action not in self.sprites.actions:
            raise ValueError(f"action must be one of {self.sprites.actions}")
        if new_action != self._action:
            self._action = new_action
            self.animation_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # compare current time to last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.animation_index += 1
        if self._action != "death" and self.animation_index >= self.sprites.num_frames(self._action):
            self.animation_index = 0
        self.image = self.sprites.parse_sprite(self._action, self.animation_index)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.get_status()
        if self.move_left:
            self.velocity.x = -self._speed
            Config.scroll = -1
        elif self.move_right:
            self.velocity.x = self._speed
            Config.scroll = -3
        elif not self.move_left and not self.move_right and not self.in_air:
            self.velocity.x = apply_friction(self.velocity.x)
            Config.scroll = -2

        if self.jump and not self.in_air:
            AudioService.jump()
            self.velocity.y = -20
            self.jump = False
            self.in_air = True
        
        if self.in_air:
            self.velocity.y += Config.GRAVITY
            if self.velocity.y > 16: # terminal velocity
                self.velocity.y = 16

        # applying velocity
        self.rect.topleft += self.velocity

        # ground collision
        if self.rect.bottom >= Config.GROUND_HEIGHT:
            self.rect.bottom = Config.GROUND_HEIGHT
            self.in_air = False
            self.velocity.y = 0

        # edge collision
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > Config.S_WIDTH:
            self.rect.right = Config.S_WIDTH

        if self._action in ["idle", "walk", "run", "death"]:
            self.rect.bottom = Config.GROUND_HEIGHT

    def hit(self):
        if self.immunity == 0:
            AudioService.hit()
            self.hp -= 1
            self.immunity = 60
            self.velocity = vec(-5, -10)
            self.jump = False
            self.in_air = True
            self.move_left = False
            self.move_right = False

    def reset(self, health: int=5):
        self.hp = health
        self.rect.topleft = self.start_pos
        self.in_air = False
        self.jump = False
        self.move_left = False
        self.move_right = False
        self.immunity = 0
        self.velocity = vec(0, 0)
        self.update_action("walk")

    def immunity_animation(self):
        if self.immunity > 0:
            self.immunity -= 1
            if self.immunity % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)

    def update(self):
        self.update_animation()
        self.move()

    def draw(self, screen: pygame.Surface, box: bool=False):
        self.immunity_animation()
        screen.blit(pygame.transform.flip(self.image, self.move_left, False), self.rect)
        if box:
            pygame.draw.rect(screen, "red", self.rect, 1)

    def death_animation(self, screen):
        self.update_action("death")
        
        self.update()
        self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        self.draw(screen)