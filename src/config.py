import time

class Config:
    FPS = 30
    S_WIDTH = 960
    S_HEIGHT = 540
    GRAVITY = 1.5
    FRICTION = 1
    VOLUME = 0.1
    GROUND_HEIGHT = S_HEIGHT - 20

class Scoreboard:
    def __init__(self):
        self._high_score = 0
        self._score = 0

    @property
    def score(self):
        return self._score
    
    @property
    def high_score(self):
        return self._high_score

    def add(self, n: int=1):
        if n >= 0 and isinstance(n, int):
            self._score += n

    def update(self):
        if self._score > self._high_score:
            self._high_score = self._score

    def reset(self):
        self._score = 0

    def draw(self, screen, font):
        text = font.render(f"Score: {self._score}", 1, "black")
        screen.blit(text, (Config.S_WIDTH//2-text.get_width()//2, 10))

    def draw_highscore(self, screen, font):
        text = font.render(f"High Score: {self._high_score}", 1, "black")
        screen.blit(text, (Config.S_WIDTH//2-text.get_width()//2, Config.S_HEIGHT//2+text.get_height()//2))

class Stopwatch:
    def __init__(self):
        self._start_time = None
        self._stop_time = None
        self._running = 0

    def start(self):
        if not self._running:
            self._start_time = time.time()
            self._running = 1
        else:
            print("Timer is running.")

    def stop(self):
        if self._running:
            self._stop_time = time.time()
            self._running = 0
        else:
            print("Timer is not running.")

    @property
    def time_elapsed(self):
        return time.time() - self._start_time

    @property
    def run_time(self):
        return self._stop_time - self._start_time
    
    def reset(self):
        if not self._running:
            self._start_time = None
            self._run_time = None
        else:
            print("Timer is in use.")

    def draw(self, screen, font):
        text = font.render(f"Time: {self.time_elapsed:.2f}s", 1, "black")
        screen.blit(text, (Config.S_WIDTH-10-text.get_width(), 10))