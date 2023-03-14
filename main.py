import pygame
from src.config import Config, Scoreboard, Stopwatch
from src.player import Player, PlayerSprites, HealthBar
from src.object import Obstacle
from src.audio import Audio
from src.world import World

def main():
    pygame.init()

    vec = pygame.math.Vector2
    screen = pygame.display.set_mode((Config.S_WIDTH, Config.S_HEIGHT))
    pygame.display.set_caption("Running Man")
    pygame.mouse.set_visible(False)
    display_font = pygame.font.Font("./assets/font/monogram.ttf", 25)

    world = World()
    scoreboard = Scoreboard()
    timer = Stopwatch()
    audio = Audio()
    health = HealthBar()
    clock = pygame.time.Clock()
    
    adventurer = PlayerSprites("./assets/adventurer/simple_adventurer.png")
    player = Player(adventurer)
    move_left, move_right = False, False

    obstacles = pygame.sprite.Group()

    def die():
        # include death animation
        timer.stop()
        scoreboard.update()

        screen_text = display_font.render(f"You played for {timer.run_time:.2f}s and scored {scoreboard.score} points!", 1, "black")
        screen.blit(screen_text, (Config.S_WIDTH/2-screen_text.get_width()/2, Config.S_HEIGHT/2-screen_text.get_height()))
        scoreboard.draw_highscore(screen, display_font)

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

    timer.start()
    audio.start_bgm()

    while run:
        clock.tick(Config.FPS)
        world.draw(screen)

        if game_paused:
            paused = display_font.render("GAME PAUSED", 1, "black")
            screen.blit(paused, (Config.S_WIDTH/2-paused.get_width()/2, Config.S_HEIGHT/2-paused.get_height()/2))
            pygame.display.update()
            pygame.time.delay(5000)
            game_paused = False
        else:
            pass

        if player.hp > 0:
            if player.jump or player.in_air:
                player.update_action("jump")
            elif move_left or move_right:
                player.update_action("walk")
            else:
                player.update_action("idle")
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
                    game_paused = True
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
        scoreboard.draw(screen, display_font)
        timer.draw(screen, display_font)
        player.draw(screen, box=False)
        health.draw(screen=screen, player_hp=player.hp)
        pygame.display.update()
    
    # exit
    pygame.quit()
    raise SystemExit    

if __name__ == "__main__":
    main()