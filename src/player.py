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

    def get_sprite(self, x: int, y: int, w: int, h: int):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        sprite = pygame.transform.scale2x(sprite)
        return sprite
    
    def parse_sprites(self, action: str):
        sprites = self.metadata[action]["sprites"]
        return sprites

    def parse_sprite(self, action: str, frame: int):
        sprites = self.parse_sprites(action)
        x, y, w, h = sprites[frame].values()
        image = self.get_sprite(x, y, w, h)
        return image
    
    def num_frames(self, action: str):
        return self.metadata[action]["frames"]

class Player(pygame.sprite.Sprite):
    def __init__(self, spritesheet: PlayerSprites):
        super().__init__()
        self._speed = 6
        self.y_vel = 0
        self.jump = False
        self.in_air = False
        self.start_pos = vec((75, 497))
        self.action = "walk"
        self.hp = 5

        # not good, reevaluate
        self.sprites = spritesheet
        self.animation_list = []
        self.animation_index = 0
        self.update_time = pygame.time.get_ticks()
        for i in range(self.sprites.num_frames(self.action)):
            img = self.sprites.parse_sprite(self.action, i)
            self.animation_list.append(img)
        self.image = self.animation_list[self.animation_index]
        self.direction = 1
        self.flip = False

        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
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

    def move(self, move_left: bool, move_right: bool):
        # reset movement
        dx = 0
        dy = 0

        if move_left:
            self.flip = True
            self.direction = -1
            dx = self._speed * self.direction
        if move_right:
            self.flip = False
            self.direction = 1
            dx = self._speed * self.direction
        if self.jump and not self.in_air:
            audio.jump_fx.play()
            self.y_vel = -20
            self.jump = False
            self.in_air = True
        
        if self.in_air:
            self.y_vel += Config.GRAVITY
            if self.y_vel > 16: # terminal velocity
                self.y_vel = 16
        dy += self.y_vel

        # check collision with edges
        if self.rect.bottom + dy >= Config.HEIGHT-5:
            self.in_air = False
            self.y_vel = 0
            dy = Config.HEIGHT-5 - self.rect.bottom
        if self.rect.left + dx <= 0:
            dx = 0
        elif self.rect.right + dx >= Config.WIDTH:
            dx = 0

        self.rect.topleft += vec(dx, dy)

    def reset(self):
        self.hp = 5
        self.rect.topleft = self.start_pos
        self.in_air = False
        self.jump = False
        self.update_action("walk")

    def draw(self, screen: pygame.Surface, box: bool=False):
        self.update_animation()
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        if box:
            pygame.draw.rect(screen, "red", self.rect, 1)