import time
import pygame

class Config:
    """Global game settings."""
    FPS = 30
    S_WIDTH = 960
    S_HEIGHT = 540
    GRAVITY = 1.5
    FRICTION = 1
    VOLUME = 0.1
    GROUND_HEIGHT = S_HEIGHT - 16
    SCROLL = -1

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
        self._high_score = 0
        self._score = 0
        self.font_color = (0, 0, 0)

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

    def update(self) -> None:
        """Updates the high score if the current score is higher."""
        if self._score > self._high_score:
            self._high_score = self._score

    def reset(self) -> None:
        """Resets the score to zero."""
        self._score = 0

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, score_type: str="score") -> None:
        """
        Draws the score on the screen using the given font.
        
        Parameters
        ---
        score: str, optional
            The score to draw: "score" or "highscore", default is "score".
        """
        if score_type == "score":
            text = font.render(f"Score: {self._score}", 1, self.font_color)
            y = 10
        elif score_type =="highscore":
            text = font.render(f"High Score: {self._high_score}", 1, self.font_color)
            y = Config.S_HEIGHT // 2 + text.get_height() // 2

        x = Config.S_WIDTH // 2 - text.get_width() // 2
        screen.blit(text, (x, y))

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
        self._start_time = None
        self._stop_time = None
        self._pause_time = None
        self._paused_duration = 0
        self._running = False

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
        text = font.render(f"Time: {self.time_elapsed:.2f}s", 1, "black")
        screen.blit(text, (Config.S_WIDTH-10-text.get_width(), 10))