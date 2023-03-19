import pygame
import logging
import os

from src.config import Config, GameState
from src.game_service import Game

def main():
    log.info("Game start.")
    pygame.init()

    # pygame event handling
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
    pygame.key.set_repeat()
    pygame.mouse.set_visible(False)

    # initialise objects
    game = Game()
    clock = pygame.time.Clock()

    while game.running:
        if Config.status is GameState.GAME_END:
            game.death()
        elif Config.status == GameState.GAME_PLAY:
            if game.paused:
                game.pause()
            else:
                game.run()
        
        pygame.display.flip()
        clock.tick(Config.FPS)
        log.debug(f"fps: {clock.get_fps()}")
    
    # exit
    log.info("Game end.")
    pygame.quit()
    raise SystemExit    

if __name__ == "__main__":
    # setup logger
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(lineno)d - %(message)s"
    log = logging.getLogger("runningman")
    log.setLevel("INFO")
    if not os.path.isdir("logs"):
        os.mkdir("logs")
    file_handler = logging.FileHandler("logs/app.log")
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    if Config.log:
        logging.disable(logging.NOTSET)
    elif Config.log is False:
        logging.disable(logging.CRITICAL)

    main()