import pygame
import json
from .config import Config
from .audio import Audio

vec = pygame.math.Vector2
audio = Audio()

class PlayerSprites:
    def __init__(self, filename: str):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(self.filename).convert()
        self.metadata_filename = self.filename.replace("png", "json")
        with open(self.metadata_filename) as f:
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
        self.action = "idle"
        self.hp = health
        self.immunity = 0
        self.direction = 1
        self.flip = False

        # not good, reevaluate
        self.sprites = spritesheet
        self.animation_index = 0
        self.update_time = pygame.time.get_ticks()

        self.image, self.mask = self.update_animation()
        self.rect = self.image.get_rect()
        self.start_pos = vec((75, Config.GROUND_HEIGHT-self.rect.height))
        self.rect.topleft = self.start_pos

    def update_action(self, new_action: str):
        if new_action != self.action:
            self.action = new_action
            self.animation_index = 0
            self.update = pygame.time.get_ticks()

    def update_animation(self):
        ANIMATION_COOLDOWN = 150
        # compare current time to last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.animation_index += 1
        if self.animation_index >= self.sprites.num_frames(self.action):
            self.animation_index = 0
        self.image = self.sprites.parse_sprite(self.action, self.animation_index)
        self.mask = pygame.mask.from_surface(self.image)
        return self.image, self.mask

    def move(self):
        if self.move_left:
            self.flip = True
            self.direction = -1
            self.velocity.x = self._speed * self.direction
        elif self.move_right:
            self.flip = False
            self.direction = 1
            self.velocity.x = self._speed * self.direction
        else:
            self.velocity.x = 0

        if self.jump and not self.in_air:
            audio.jump()
            self.velocity.y = -20
            self.jump = False
            self.in_air = True
        
        if self.in_air:
            self.velocity.y += Config.GRAVITY
            if self.velocity.y > 16: # terminal self.velocity
                self.velocity.y = 16

        self.rect.topleft += self.velocity

        # edge collision
        if self.rect.bottom >= Config.GROUND_HEIGHT:
            self.rect.bottom = Config.GROUND_HEIGHT
            self.in_air = False
            self.velocity.y = 0

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > Config.S_WIDTH:
            self.rect.right = Config.S_WIDTH

        if self.action in ["idle", "walk", "run"]:
            self.rect.y = Config.GROUND_HEIGHT - self.image.get_height()

    def reset(self, health: int=5):
        self.hp = health
        self.rect.topleft = self.start_pos
        self.in_air = False
        self.jump = False
        self.move_left = False
        self.move_right = False
        self.immunity = 0
        self.update_action("idle")

    def draw(self, screen: pygame.Surface, box: bool=False):
        self.update_animation()
        if self.immunity > 0:
            self.immunity -= 1
            if self.immunity % 10 < 5:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)


        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        if box:
            pygame.draw.rect(screen, "red", self.rect, 1)

class HealthBar():
    def __init__(self, max_health: int=5):
        self.__max_health = max_health
        self.__heart = pygame.image.load("./assets/images/heart.png").convert_alpha()
        self.__heart = pygame.transform.scale2x(self.__heart)
        self.__damage = pygame.image.load("./assets/images/heart_damage.png").convert_alpha()
        self.__damage = pygame.transform.scale2x(self.__damage)

    def draw(self, screen, player_hp):
        for point in range(player_hp):
            screen.blit(self.__heart, (10 + point*25, 10))
        for point in range(self.__max_health - player_hp):
            screen.blit(self.__damage, (10 + player_hp*25 + point*25, 10))
