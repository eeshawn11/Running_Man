import pygame
import json
from .config import Config
from .audio import Audio
from . import utils

vec = pygame.math.Vector2
audio = Audio()

class PlayerSprites:
    def __init__(self, filename: str):
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
        x, y, w, h = sprites[frame].values()
        image = self.get_sprite(x, y, w, h)
        return image


class Player(pygame.sprite.Sprite):
    def __init__(self, spritesheet: PlayerSprites, health: int=5):
        super().__init__()
        self._speed = 6
        self.velocity = vec(0, 0)
        self.jump = False
        self.in_air = False
        self.move_left = False
        self.move_right = False
        self._action = "idle"
        self.hp = health
        self.immunity = 0
        self._direction = 1
        self._flip = False

        # not good, reevaluate
        self.sprites = spritesheet
        self.animation_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image, self.mask = self.update_animation()
        self.rect = self.image.get_rect()
        self.start_pos = vec((75, Config.GROUND_HEIGHT-self.rect.height))
        self.rect.topleft = self.start_pos

    def update_action(self, new_action: str):
        if new_action != self._action:
            self._action = new_action
            self.animation_index = 0
            self.update = pygame.time.get_ticks()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        # compare current time to last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.animation_index += 1
        if self.animation_index >= self.sprites.num_frames(self._action):
            self.animation_index = 0
        self.image = self.sprites.parse_sprite(self._action, self.animation_index)
        self.mask = pygame.mask.from_surface(self.image)
        return self.image, self.mask
    
    def hit(self):
        if self.immunity == 0:
            audio.hit()
            self.hp -= 1
            self.immunity = 60
            self.velocity = vec(-5, -10)
            self.jump = False
            self.in_air = True
            self.move_left = False
            self.move_right = False
            self.move()

    def move(self):
        if self.move_left:
            self._flip = True
            self._direction = -1
            self.velocity.x = self._speed * self._direction
        elif self.move_right:
            self._flip = False
            self._direction = 1
            self.velocity.x = self._speed * self._direction
        elif not self.move_left and not self.move_right and not self.in_air:
            self.velocity.x = utils.apply_friction(self.velocity.x)

        if self.jump and not self.in_air:
            audio.jump()
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

    def reset(self, health: int=5):
        self.hp = health
        self.rect.topleft = self.start_pos
        self.in_air = False
        self.jump = False
        self.move_left = False
        self.move_right = False
        self.immunity = 0
        self.velocity = vec(0, 0)
        self.update_action("idle")

    def draw(self, screen: pygame.Surface, box: bool=False):
        self.update_animation()
        if self._action in ["idle", "walk", "run"]:
            self.rect.y = Config.GROUND_HEIGHT - self.image.get_height()
        if self.immunity > 0:
            self.immunity -= 1
            if self.immunity % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)


        screen.blit(pygame.transform.flip(self.image, self._flip, False), self.rect)
        if box:
            pygame.draw.rect(screen, "red", self.rect, 1)

class HealthBar():
    def __init__(self, max_health: int=5):
        self.__max_health = max_health
        self.__heart = utils.load_and_scale_image("./assets/images/heart.png", True)
        self.__damage = utils.load_and_scale_image("./assets/images/heart_damage.png", True)

    def draw(self, screen: pygame.Surface, player_hp: int):
        if player_hp > self.__max_health:
            player_hp = self.__max_health
        for point in range(player_hp):
            screen.blit(self.__heart, (10 + point*25, 10))
        for point in range(self.__max_health - player_hp):
            screen.blit(self.__damage, (10 + player_hp*25 + point*25, 10))
