import pygame
import random
import logging

from .config import Config, GameState
from .player import Player
from .obstacle import *
from .audio_service import AudioService
from .visuals import Tile, Grass, Bush, Tree, Background
from .utils import Scoreboard, Stopwatch, HealthBar

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

        self.running = True
        self.paused = False
        self.speed_up_count = 0

        AudioService.start_bgm()
        self.timer.start()
        self.logger.info("Game initialised")

    def setup(self):
        self.logger.info("Game.setup start")
        bg1 = Background(0, 0)
        bg2 = Background(Config.S_WIDTH, 0)
        self.backgrounds = [bg1, bg2]

        self.rear = pygame.sprite.Group()
        self.fore = pygame.sprite.Group()
        self.ground = pygame.sprite.Group()
        self.trees = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        tile = Tile()
        for i in range(80):
            tile.rect.topleft = (i * tile.width * 0.8, Config.GROUND_HEIGHT)
            next_tile = Tile()
            next_tile.prev = tile
            self.ground.add(tile)
            tile = next_tile
        
        for i in range(8):
            bush = Bush()
            bush.rect.bottomleft = (
                (i * bush.width) + random.randint(50, 100),
                Config.GROUND_HEIGHT
                )
            self.rear.add(bush)

        for i in range(70):
            grass = Grass()
            grass.rect.bottomleft = (
                (i * tile.width) - random.randint(0, 20), 
                Config.GROUND_HEIGHT + random.randint(0, 5)
                )
            self.fore.add(grass)

        tree = Tree()
        tree.rect.midbottom = (random.choice([400, 450, 500]), Config.GROUND_HEIGHT)
        self.trees.add(tree)
        self.last_tree = tree

        obstacle = Obstacle.gen()
        obstacle.rect.bottomleft = (Config.S_WIDTH, Config.GROUND_HEIGHT)
        self.obstacles.add(obstacle)
        self.last_obstacle = obstacle

        self.logger.info("Game.setup complete")

    def update(self):
        self.logger.debug("Game.update start")
        for bg in self.backgrounds:
            bg.update()
        self.rear.update()
        self.trees.update()
        if Config.S_WIDTH - self.last_tree.rect.right > random.randrange(800, 1500, 100):
            new_tree = Tree()
            new_tree.rect.bottomleft = (Config.S_WIDTH, Config.GROUND_HEIGHT)
            self.last_tree = new_tree
            self.trees.add(new_tree)
        self.fore.update()
        self.ground.update()
        self.logger.debug("Game.update complete")

    def draw(self):
        self.logger.debug("Game.draw start")
        for bg in self.backgrounds:
            bg.draw(self.screen)
        self.rear.draw(self.screen)
        self.trees.draw(self.screen)
        self.player.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.fore.draw(self.screen)
        self.ground.draw(self.screen)

        self.scoreboard.draw(self.screen, self.display_font)
        self.timer.draw(self.screen, self.display_font)
        self.health.draw(self.screen, self.player.hp)
        self.logger.debug("Game.draw complete")

    def check_input(self):

        def check_exit_key(event):
            if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key in Config.exit_keybind
                ):
                self.logger.info(f"Game.exit_input {event.type}")
                return True
            return False

        def check_pause_key(event):
            if event.type == pygame.KEYDOWN and event.key in Config.pause_keybind:
                self.logger.info(f"Game.pause_input {event.key}")
                return True
            return False

        for event in pygame.event.get():
            if check_exit_key(event):
                self.running = False

            if Config.status is GameState.GAME_PLAY:
                if check_pause_key(event):
                    self.toggle_pause()
            elif Config.status is GameState.GAME_END:
                if check_pause_key(event):
                    self.reset()

    def toggle_pause(self):
        if not self.paused:
            self.logger.info("Game paused")
            self.paused = True
            self.timer.pause()
            AudioService.pause_bgm()
        elif self.paused:
            self.logger.info("Game unpaused")
            self.paused = False
            self.timer.resume()
            AudioService.resume_bgm()

    def speed_up(self):
        """Speeds up the game at specified intervals."""
        interval = 5
        time_elapsed = int(self.timer.time_elapsed)
        if time_elapsed % interval == 0 and self.speed_up_count < time_elapsed // interval:
            self.speed_up_count += 1
            Config.BASE_SCROLL -= 1
            self.logger.info(f"{self.timer.time_elapsed} elapsed, new speed {Config.BASE_SCROLL}")

    def run(self):
        self.check_input()
        print(Config.scroll)

        #obstacle creation
        if len(self.obstacles.sprites()) < 3 and self.last_obstacle.rect.x < Config.S_WIDTH * random.uniform(0.5, 0.8):
            obstacle = Obstacle.gen()
            self.obstacles.add(obstacle)
            self.last_obstacle = obstacle
            self.logger.debug(f"New {obstacle} generated")

        if pygame.sprite.spritecollideany(self.player, self.obstacles, pygame.sprite.collide_mask):
            for obstacle in pygame.sprite.spritecollide(self.player, self.obstacles, False, pygame.sprite.collide_mask):
                self.player.hit()

        self.player.update()

        self.obstacles.update()
        for obstacle in self.obstacles:
            if obstacle.check_score():
                self.scoreboard.add()
                AudioService.score()

        self.speed_up()
        self.update()
        self.draw()

        if self.player.hp == 0:
            Config.status = GameState.GAME_END
            self.timer.stop()
    
    def pause(self):
        self.check_input()
        paused = self.display_font.render("GAME PAUSED", 1, "black")
        self.screen.blit(paused, (Config.S_WIDTH/2-paused.get_width()/2, Config.S_HEIGHT/2-paused.get_height()/2))

    def death(self):
        self.check_input()
        self.draw()
        AudioService.fade_bgm()
        self.scoreboard.update_highscore()
        self.player.death_animation(self.screen)

    def reset(self):
        self.logger.info("Game.reset start")
        self.player.reset()
        self.scoreboard.reset()
        self.obstacles.empty()
        
        Config.status = GameState.GAME_PLAY
        Config.BASE_SCROLL = -5
        self.setup()
        self.timer.reset()
        self.timer.start()
        AudioService.start_bgm()
        self.logger.info("Game.reset complete")