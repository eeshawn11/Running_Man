import pygame
import random

from src.config import Config, Scoreboard, Stopwatch
from src.world import World
from src.player import Player, HealthBar
from src.obstacle import Obstacle
from src.audio import Audio

def main():
    pygame.init()

    # pygame event handling
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    pygame.key.set_repeat()
    pygame.mouse.set_visible(False)

    vec = pygame.math.Vector2
    # set up display
    screen = pygame.display.set_mode((Config.S_WIDTH, Config.S_HEIGHT))
    pygame.display.set_caption("Running Man")
    display_font = pygame.font.Font("./assets/font/monogram.ttf", 25)

    # initialise objects
    world = World()
    scoreboard = Scoreboard()
    timer = Stopwatch()
    audio = Audio()
    health = HealthBar()
    clock = pygame.time.Clock()
    player = Player()
    obstacles = pygame.sprite.Group()

    def die():
        # include death animation
        timer.stop()
        scoreboard.update()
        audio.fade_bgm()

        screen_text = display_font.render(f"You played for {timer.run_time:.2f}s and scored {scoreboard.score} points!", 1, "black")
        screen.blit(screen_text, (Config.S_WIDTH/2-screen_text.get_width()/2, Config.S_HEIGHT/2-screen_text.get_height()))
        scoreboard.draw(screen, display_font, "highscore")

        pygame.display.flip()
        pygame.time.delay(3000)

        # reset game
        player.reset()
        scoreboard.reset()
        timer.reset()
        obstacles.empty()
        timer.start()
        audio.start_bgm()

    running = True
    game_paused = False

    audio.start_bgm()
    timer.start()

    while running:
        clock.tick(Config.FPS)
        world.draw(screen)

        if game_paused:
            timer.pause()
            paused = display_font.render("GAME PAUSED", 1, "black")
            screen.blit(paused, (Config.S_WIDTH/2-paused.get_width()/2, Config.S_HEIGHT/2-paused.get_height()/2))
            pygame.display.update()
            pygame.time.delay(5000)
            timer.resume()
            game_paused = False
        elif player.hp <= 0:
            player.update_action("death")
            die()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # exit
                running = False
            # key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # exit
                    running = False
                if event.key == pygame.K_e: # pause
                    game_paused = True
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.jump = True
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.move_left = True
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.move_right = True
            # key release
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.move_left = False
                    player._flip = False
                    player._direction = 1
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.move_right = False

        if player.jump or player.in_air:
            player.update_action("jump")
        elif player.move_left or player.move_right:
            player.update_action("run")
        else:
            player.update_action("walk")

        #obstacle creation
        # if len(obstacles) < random.randint(0,3):
        #     obstacle = Obstacle()
        #     obstacles.add(obstacle)

        if pygame.sprite.spritecollideany(player, obstacles, pygame.sprite.collide_mask):
            for obstacle in pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
                if player.rect.bottom >= obstacle.rect.top and player.rect.right < obstacle.rect.centerx - 30:
                    player.hit()

        player.move()

        obstacles.update()
        for obstacle in obstacles:
            if obstacle.rect.right <= 0:
                scoreboard.add()
                audio.point()
                obstacle.reset()
        obstacles.draw(screen)

        # draw and update display
        scoreboard.draw(screen, display_font)
        timer.draw(screen, display_font)
        player.draw(screen)
        health.draw(screen, player.hp)
        pygame.display.flip()
    
    # exit
    pygame.quit()
    raise SystemExit    

if __name__ == "__main__":
    main()