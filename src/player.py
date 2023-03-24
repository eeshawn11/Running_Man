import pygame
import logging

from .config import Config
from .audio_service import AudioService
from .visuals import PlayerSprites

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    base_health = 3

    def __init__(self, health: int=base_health):
        super().__init__()
        self.logger = logging.getLogger("runningman.player.Player")
        self._speed = 3
        self.hp = health
        self.start_pos = (75, Config.GROUND_HEIGHT)

        # player status
        self.immunity = 0
        self._action = "walk"
        self.velocity = vec(0, 0)
        self.in_air = False

        # player sprite
        self.sprites = PlayerSprites()
        self.animation_index = 0
        self.update_time = pygame.time.get_ticks()
        self.update_animation()
        self.rect = self.image.get_rect(bottomleft=self.start_pos)
        self.logger.info("Player object initialised")

    def get_status(self):
        self.logger.debug(f"hp: {self.hp}, in_air: {self.in_air}, velocity: {self.velocity}")
        if self.hp > 0:
            if self.in_air:
                self.update_action("jump")
            elif self.velocity.x != 0:
                self.update_action("fast")
            else:
                self.update_action("run")

    def update_action(self, new_action: str):
        self.logger.debug(f"player.update_action({new_action})")
        if new_action not in self.sprites.actions:
            raise ValueError(f"action must be one of {self.sprites.actions}")
        if new_action != self._action:
            self._action = new_action
            self.animation_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        self.logger.debug("player.update_animation")
        ANIMATION_COOLDOWN = 100
        # compare current time to last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.animation_index += 1
            self.logger.debug("player.animation_index += 1")
        if self._action != "death" and self.animation_index >= self.sprites.num_frames(self._action):
            self.animation_index = 0
        self.image = self.sprites.parse_sprite(self._action, self.animation_index)
        self.mask = pygame.mask.from_surface(self.image)

    def move(self):
        self.logger.debug("player.move")
        keys = pygame.key.get_pressed()

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

        if keys[Config.left_keybind]:
            self.logger.debug("left input detected")
            self.velocity.x = -self._speed
            Config.scroll = Config.BASE_SCROLL + self._speed
        elif keys[Config.right_keybind]:
            self.logger.debug("right input detected")
            self.velocity.x = self._speed
            Config.scroll = Config.BASE_SCROLL - self._speed
        elif not self.in_air:
            self.logger.debug(f"player.in_air {self.in_air}, apply friction")
            self.velocity.x = apply_friction(self.velocity.x)
            Config.scroll = Config.BASE_SCROLL

        # jump
        if keys[Config.up_keybind] and not self.in_air:
            self.logger.debug("jump input detected")
            AudioService.jump()
            self.velocity.y = -20
            self.in_air = True
        
        # apply gravity
        if self.in_air:
            self.logger.debug(f"player.in_air {self.in_air}, apply gravity")
            self.velocity.y += Config.GRAVITY
            if self.velocity.y > 16: # terminal velocity
                self.velocity.y = 16

        # applying velocity
        self.rect.topleft += self.velocity
        self.logger.debug(f"player.move({self.velocity})")

    def hit(self):
        if self.immunity == 0:
            AudioService.hit()
            self.hp -= 1
            self.immunity = 60
            self.velocity = vec(-5, -10)
            self.in_air = True

    def reset(self, health: int=base_health):
        self.hp = health
        self.rect.topleft = self.start_pos
        self.in_air = False
        self.immunity = 0
        self.velocity = vec(0, 0)
        self.update_action("run")

    def immunity_animation(self):
        if self.immunity > 0:
            self.immunity -= 1
            if self.immunity % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)

    def update(self):
        self.move()
        self.get_status()
        self.update_animation()

    def draw(self, screen: pygame.Surface, box: bool=False):
        self.immunity_animation()
        # ground collision
        if self.rect.bottom >= Config.GROUND_HEIGHT:
            self.logger.debug(f"player collide with ground")
            self.rect.bottom = Config.GROUND_HEIGHT
            self.in_air = False
            self.velocity.y = 0

        # edge collision
        if self.rect.left < 0:
            self.logger.debug("player collide left")
            self.rect.left = 0
        elif self.rect.right > Config.S_WIDTH:
            self.logger.debug("player collide right")
            self.rect.right = Config.S_WIDTH

        flip_x = self.velocity.x < 0
        screen.blit(pygame.transform.flip(self.image, flip_x, False), self.rect)
        if box:
            pygame.draw.rect(screen, "red", self.rect, 1)

    def death_animation(self, screen):
        self.update_action("death")
        
        self.update()
        self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        self.draw(screen)