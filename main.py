import pygame
import time
import random

from src.config import Config, Scoreboard, Stopwatch
from src.player import Player, PlayerSprites
from src.object import Obstacle


pygame.init()

vec = pygame.math.Vector2
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Running Man")
pygame.mouse.set_visible(False)
display_font = pygame.font.Font("./assets/font/monogram.ttf", 25)

def draw(scoreboard, timer, clock):
    time_text = display_font.render(f"Time: {timer.time_elapsed:.2f}s", 1, "black")
    score_text = display_font.render(f"Score: {scoreboard.score}", 1, "black")
    fps_text = display_font.render(f"FPS: {clock.get_fps():.0f}", 1, "black")

    screen.blits(
        blit_sequence=(
            (time_text, (10,10)),
            (score_text, (Config.WIDTH//2-score_text.get_width()//2, 10)),
            (fps_text, (Config.WIDTH-10-fps_text.get_width(), 10)),
        )
    )

def main():
    background = pygame.image.load("./assets/background/background_lake.jpg").convert()

    scoreboard = Scoreboard()
    clock = pygame.time.Clock()
    timer = Stopwatch()
    timer.start()
    
    adventurer = PlayerSprites("./assets/adventurer/simple_adventurer.png")
    player = Player(adventurer)
    move_left, move_right = False, False

    obstacles = pygame.sprite.Group()

    def die():
        # stop movement and death animation
        timer.stop()
        scoreboard.check()

        screen_text = display_font.render(f"You played for {timer.run_time:.2f}s and scored {scoreboard.score} points!", 1, "black")
        screen.blit(screen_text, (Config.WIDTH/2-screen_text.get_width()/2, Config.HEIGHT/2-screen_text.get_height()))
        highscore_text = display_font.render(f"High Score: {scoreboard.high_score}", 1, "black")
        screen.blit(highscore_text, (Config.WIDTH/2-highscore_text.get_width()/2, Config.HEIGHT/2+highscore_text.get_height()/2))

        pygame.display.update()
        pygame.time.delay(3000)

        # reset game
        player.reset()
        scoreboard.reset()
        timer.reset()
        timer.start()
        obstacles.empty()

    run = True
    game_paused = False
    while run:
        clock.tick(Config.FPS)

        screen.blit(background, (0,0))
        pygame.draw.line(screen, "red", (0,Config.HEIGHT-5), (Config.WIDTH, Config.HEIGHT-5))

        if game_paused:
            screen.blit(background, (0,0))
            time.sleep(5)
            game_paused = False
        else:
            pass

        if player.hp > 0:
            if player.jump or player.in_air:
                player.update_action("jump")
            else:
                player.update_action("walk")
            player.move(move_left, move_right)
        else:
            player.update_action("death")
            die()

        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                run = False
            # key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                if event.key == pygame.K_w:
                    player.jump = True
                if event.key == pygame.K_a:
                    move_left = True
                if event.key == pygame.K_d:
                    move_right = True
                if event.key == pygame.K_e:
                    timer.stop()
                    player.hp = 0
                if event.key == pygame.K_SPACE:
                    game_paused = True
            # key release
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    move_left = False
                if event.key == pygame.K_d:
                    move_right = False

        #obstacle creation
        if len(obstacles) < 3:
            obstacle = Obstacle()
            obstacles.add(obstacle)
        
        # obstacle movement
        for obstacle in obstacles:
            if player.mask.overlap(obstacle.mask, (vec(obstacle.rect[:2]) - vec(player.rect[:2]))):
                # only hit once per object
                if obstacle.hit:
                    player.hp -= 1
                    obstacle.hit = False
            obstacle.move()
            if obstacle.rect.right <= 0:
                scoreboard.add()
                obstacles.remove(obstacle)
                del obstacle
                break
            obstacle.draw(screen, box=True)

        # draw and update display
        player.draw(screen, box=True)
        draw(scoreboard, timer, clock)
        pygame.display.update()
    
    # exit
    pygame.quit()
    raise SystemExit    

if __name__ == "__main__":
    main()