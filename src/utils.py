import pygame
import time
import logging

from .config import Config, GameState
from .visuals import Heart

class Scoreboard:
    """
    A utility class for managing the game's score and high score.

    Methods
    -------
    add(n: int=1) -> None
        Adds the given value to the score.
    update() -> None
        Updates the high score if the current score is higher.
    reset() -> None
        Resets the score to zero.
    draw(screen: pygame.Surface, font: pygame.font.Font, score: str="score") -> None
        Draws the score or high score on the screen using the given font.
    """
    def __init__(self):
        self.logger = logging.getLogger("runningman.utils.Scoreboard")
        self._high_score = 0
        self._score = 0
        self.font_color = (0, 0, 0)
        self.logger.debug("Scoreboard initialised.")

    @property
    def score(self) -> int:
        """int: The current score."""
        return self._score
    
    @property
    def high_score(self) -> int:
        """int: The highest score achieved this session."""
        return self._high_score

    def add(self, n: int=1) -> None:
        """Adds the given value, n to the score. Default n = 1."""
        if not isinstance(n, int) and n < 0:
            raise ValueError("n must be a positive integer.")
        self._score += n

    def update_highscore(self) -> None:
        """Updates the high score if the current score is higher."""
        if self._score > self._high_score:
            self._high_score = self._score
            self.logger.info(f"New high score: {self._high_score}")

    def reset(self) -> None:
        """Resets the score to zero."""
        self._score = 0
        self.logger.debug("Scoreboard.score reset.")

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Draws the score on the screen using the given font.
        
        Parameters
        ---
        score: str, optional
            The score to draw: "score" or "highscore", default is "score".
        """
        if Config.status is GameState.GAME_PLAY:
            text = font.render(f"Score: {self._score}", 1, self.font_color)
            y = 10
            x = Config.S_WIDTH // 2 - text.get_width() // 2
            screen.blit(text, (x, y))
        elif Config.status is GameState.GAME_END:
            score_text = font.render(f"Score: {self._score}", 1, self.font_color)
            score_pos = (Config.S_WIDTH // 2 - score_text.get_width() // 2, 10)
            highscore_text = font.render(f"High Score: {self._high_score}", 1, self.font_color)
            highscore_pos = (
                Config.S_WIDTH // 2 - highscore_text.get_width() // 2, 
                Config.S_HEIGHT // 2 + highscore_text.get_height() // 2
                )

            screen.blits(blit_sequence=((score_text, score_pos), (highscore_text, highscore_pos)))

class Stopwatch:
    """
    A utility class for measuring elapsed time in the game.

    Methods
    ---
    start() -> None
        Starts the stopwatch.
    pause() -> None
        Pauses a running stopwatch.
    resume() -> None
        Resumes a paused stopwatch.
    stop() -> None
        Stops a running stopwatch.
    reset() -> None
        Resets a stopped stopwatch.
    time_elapsed() -> float
        Returns the time elapsed while stopwatch is still running.
    run_time() -> float
        Returns the run time after stopwatch has stopped.
    """
    def __init__(self) -> None:
        self.logger = logging.getLogger("runningman.utils.Stopwatch")
        self._start_time = None
        self._stop_time = None
        self._pause_time = None
        self._paused_duration = 0
        self._running = False
        self.logger.debug("Stopwatch initialised.")

    def start(self) -> None:
        """Starts the stopwatch if it is not running."""
        if self._running or self._pause_time:
            raise RuntimeError("Stopwatch is already running.")
        self._start_time = time.time()
        self._running = True

    def stop(self) -> None:
        """Stops the stopwatch if it is running."""
        if not self._running:
            raise RuntimeError("Stopwatch is not running.")
        self._stop_time = time.time()
        self._running = False
        self._pause_time = None

    def pause(self) -> None:
        """Pauses the stopwatch while it is running."""
        if not self._running:
            raise RuntimeError("Stopwatch is not running.")
        elif self._pause_time:
            raise RuntimeError("Stopwatch is already paused.")
        else:
            self._pause_time = time.time()

    def resume(self) -> None:
        """Resumes the stopwatch if it is paused."""
        if not self._pause_time:
            raise RuntimeError("Stopwatch is not paused.")
        self._paused_duration += time.time() - self._pause_time
        self._pause_time = None

    @property
    def time_elapsed(self) -> float:
        """Returns the time elapsed while stopwatch is still running."""
        if not self._running:
            raise RuntimeError("Stopwatch is not running, use run_time() instead for previous run time.")
        return time.time() - self._start_time - self._paused_duration

    @property
    def run_time(self) -> float:
        """Returns the total run time after stopwatch has stopped."""
        if self._running:
            raise RuntimeError("Stopwatch is still running, use time_elapsed() instead.")
        return self._stop_time - self._start_time - self._paused_duration

    def reset(self) -> None:
        """Resets the stopwatch."""
        if self._running:
            raise RuntimeError("Stopwatch is still in use.")
        self._start_time = None
        self._run_time = None
        self._pause_time = None
        self._paused_duration = 0

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draws the time on the screen using the given font."""
        if Config.status is GameState.GAME_PLAY:
            text = font.render(f"Time: {self.time_elapsed:.2f}s", 1, "black")
        elif Config.status is GameState.GAME_END:
            text = font.render(f"Time: {self.run_time:.2f}s", 1, "black")
        screen.blit(text, (Config.S_WIDTH-10-text.get_width(), 10))

class HealthBar():
    def __init__(self, max_health: int=3):
        self.logger = logging.getLogger("runningman.utils.HealthBar")
        self.__max_health = max_health
        self.hearts = pygame.sprite.Group()

        for point in range(self.__max_health):
            heart = Heart()
            heart.rect.topleft = (10 + point*25, 10)
            self.hearts.add(heart)

        self.logger.debug("HealthBar initialised.")

    def draw(self, screen: pygame.Surface, player_hp: int):
        if player_hp > self.__max_health:
            player_hp = self.__max_health

        for idx, heart in enumerate(self.hearts):
            if idx+1 <= player_hp:
                heart.image.set_alpha(255)
            else:
                heart.image.set_alpha(100)

        self.hearts.draw(screen)