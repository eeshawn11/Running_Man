import pygame
import random
import logging

log = logging.getLogger("runningman.game_service")

from .config import Config, GameState
from .player import Player
from .obstacle import Obstacle
from .audio_service import AudioService
from .visuals import load_background, Tile, Grass, Lamp, Tree
from .utils import Scoreboard, Stopwatch, HealthBar

def check_exit_key(event):
    if event.type == pygame.QUIT:
        log.info(f"exit input {event.type}")
        return True
    if event.type == pygame.KEYDOWN and event.key in Config.exit_keybind:
        log.info(f"exit input {event.key}")
        return True
    return False

def check_pause_key(event):
    if event.type == pygame.KEYDOWN and event.key in Config.pause_keybind:
        log.info(f"pause input {event.key}")
        return True
    return False

class Game:
    def __init__(self):
        # set up display
        self.logger = logging.getLogger("runningman.game_service.Game")
        self.screen = pygame.display.set_mode((Config.S_WIDTH, Config.S_HEIGHT))
        pygame.display.set_caption("Running Man")
        self.setup()

        # initialise objects
        self.player = Player()
        self.display_font = pygame.font.Font("./assets/font/monogram.ttf", 25)
        self.health = HealthBar()
        self.scoreboard = Scoreboard()
        self.timer = Stopwatch()
        self.obstacles = pygame.sprite.Group()

        self.running = True
        self.paused = False

        AudioService.start_bgm()
        self.timer.start()
        self.logger.info("Game object initialised")

    def setup(self):
        self.logger.info("game setup start")
        self.background = load_background()

        self.rear_grass = pygame.sprite.Group()
        self.fore_grass = pygame.sprite.Group()
        self.lamp_posts = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()

        for i in range(100):
            tile = Tile()
            tile.rect.topleft = (i * tile.width * 0.8, Config.GROUND_HEIGHT)
            self.ground.add(tile)
        
        for i in range(21):
            grass = Grass()
            grass.rect.bottomleft = (
                (i * grass.width) - random.randint(0, 20), 
                Config.GROUND_HEIGHT + random.randint(0, 2)
                )
            self.rear_grass.add(grass)

        for i in range(17):
            grass = Grass()
            grass.rect.bottomleft = (
                (i * grass.width) - random.randint(0, 20), 
                Config.GROUND_HEIGHT + random.randint(3, 6)
                )
            self.fore_grass.add(grass)
        
        lamps = 2
        for i in range(lamps):
            lamp = Lamp()
            distance_btw_lamps = Config.S_WIDTH // lamps
            lamp.rect.bottomleft = (i * distance_btw_lamps, Config.GROUND_HEIGHT)
            self.lamp_posts.add(lamp)

        tree = Tree()
        tree.rect.midbottom = (random.choice([350, 400, 450]), Config.GROUND_HEIGHT)
        self.trees.add(tree)
        self.last_tree = tree
        self.logger.info("game setup complete")

    def update(self):
        self.logger.debug("update start")
        self.rear_grass.update()
        self.trees.update()
        if Config.S_WIDTH - self.last_tree.rect.right > random.choice([450, 500, 550]):
            new_tree = Tree()
            new_tree.rect.bottomleft = (Config.S_WIDTH, Config.GROUND_HEIGHT)
            self.last_tree = new_tree
            self.trees.add(new_tree)
        self.lamp_posts.update()
        self.fore_grass.update()
        self.ground.update()
        self.logger.debug("update complete")

    def draw(self):
        self.logger.debug("game.draw() start")
        self.screen.blit(self.background, (0, 0))
        self.rear_grass.draw(self.screen)
        self.trees.draw(self.screen)
        self.lamp_posts.draw(self.screen)
        self.fore_grass.draw(self.screen)
        self.ground.draw(self.screen)

        self.scoreboard.draw(self.screen, self.display_font)
        self.timer.draw(self.screen, self.display_font)
        self.player.draw(self.screen)
        self.health.draw(self.screen, self.player.hp)
        self.logger.debug("game.draw() complete")

    def check_input(self):
        for event in pygame.event.get():
            if check_exit_key(event):
                self.running = False

            if Config.status is GameState.GAME_PLAY:
                if check_pause_key(event):
                    self.toggle_pause()
                if event.type == pygame.KEYDOWN:
                    log.info(f"keydown {event.key}")
                    if event.key in Config.up_keybind:
                        self.player.jump = True
                    if event.key in Config.left_keybind:
                        self.player.move_left = True
                    if event.key in Config.right_keybind:
                        self.player.move_right = True
                if event.type == pygame.KEYUP:
                    log.info(f"keyup {event.key}")
                    if event.key in Config.left_keybind:
                        self.player.move_left = False
                    if event.key in Config.right_keybind:
                        self.player.move_right = False
            elif Config.status is GameState.GAME_END:
                if check_pause_key(event):
                    self.reset()

    def toggle_pause(self):
        if not self.paused:
            self.logger.info("game paused")
            self.paused = True
            self.timer.pause()
            AudioService.pause_bgm()
        elif self.paused:
            self.logger.info("game unpaused")
            self.paused = False
            self.timer.resume()
            AudioService.resume_bgm()

    def run(self):
        self.check_input()

        #obstacle creation
        if len(self.obstacles) < random.randint(0,3):
            obstacle = Obstacle()
            self.obstacles.add(obstacle)

        if pygame.sprite.spritecollideany(self.player, self.obstacles, pygame.sprite.collide_mask):
            for obstacle in pygame.sprite.spritecollide(self.player, self.obstacles, False, pygame.sprite.collide_mask):
                if self.player.rect.bottom >= obstacle.rect.top and self.player.rect.right < obstacle.rect.centerx - 30:
                    self.player.hit()

        self.player.update()

        self.obstacles.update()
        for obstacle in self.obstacles:
            if obstacle.rect.right <= 0:
                self.scoreboard.add()
                AudioService.score()
                obstacle.reset()

        self.update()
        self.draw()
        self.obstacles.draw(self.screen)

        if self.player.hp == 0:
            Config.status = GameState.GAME_END
            self.timer.stop()
    
    def pause(self):
        self.check_input()

        # overlay = pygame.Surface((Config.S_WIDTH, Config.S_HEIGHT), pygame.SRCALPHA)
        # overlay.fill((211,211,211, 5))
        # self.screen.blit(overlay, (0, 0))
        paused = self.display_font.render("GAME PAUSED", 1, "black")
        self.screen.blit(paused, (Config.S_WIDTH/2-paused.get_width()/2, Config.S_HEIGHT/2-paused.get_height()/2))

    def death(self):
        self.check_input()
        self.draw()
        AudioService.fade_bgm()
        self.scoreboard.update_highscore()
        self.player.death_animation(self.screen)

    def reset(self):
        self.logger.info("game reset start")
        self.player.reset()
        self.scoreboard.reset()
        self.obstacles.empty()
        
        Config.status = GameState.GAME_PLAY
        self.setup()
        self.timer.reset()
        self.timer.start()
        AudioService.start_bgm()
        self.logger.info("game reset complete")