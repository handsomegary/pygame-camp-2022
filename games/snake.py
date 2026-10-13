"""The camp's Snake game, with a Pygame-free model and drawn artwork.

The lecture uses a 720 x 630 canvas, 30-pixel cells and ten moves per
second. These rules are preserved while input and drawing run at 60 FPS.
"""

from __future__ import annotations

from array import array
from collections import deque
from enum import Enum
import math
import random
from typing import Any


Cell = tuple[int, int]


class Direction(Enum):
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    UP = (0, -1)

    @property
    def opposite(self) -> Direction:
        dx, dy = self.value
        return Direction((-dx, -dy))


class GameState(str, Enum):
    RUNNING = "running"
    LOST = "lost"
    WON = "won"


class SnakeGame:
    """Grid-based game rules; importing or testing this needs no Pygame.

    ``body`` stores cells with the head first. ``tick()`` advances exactly
    one cell and returns whether a fruit was eaten. Input is buffered for
    at most two turns so quick corners work without permitting a reversal.
    """

    def __init__(
        self,
        columns: int = 24,
        rows: int = 21,
        *,
        initial_length: int = 3,
        rng: random.Random | None = None,
    ) -> None:
        if columns < 1 or rows < 1:
            raise ValueError("The board dimensions must be positive.")
        if initial_length < 1:
            raise ValueError("The initial length must be positive.")
        self.columns = columns
        self.rows = rows
        self.initial_length = min(initial_length, columns)
        self.rng = rng if rng is not None else random.Random()
        self.body: list[Cell] = []
        self._turns: deque[Direction] = deque()
        self.direction = Direction.RIGHT
        self.fruit: Cell | None = None
        self.state = GameState.RUNNING
        self.score = 0
        self.collision_at: Cell | None = None
        self.reset()

    @property
    def head(self) -> Cell:
        return self.body[0]

    @property
    def alive(self) -> bool:
        return self.state is GameState.RUNNING

    def reset(self) -> None:
        """Start a fresh round and keep the supplied random generator."""
        y = self.rows // 2
        self.body = [(x, y) for x in range(self.initial_length - 1, -1, -1)]
        self._turns.clear()
        self.direction = Direction.RIGHT
        self.score = 0
        self.collision_at = None
        self.state = GameState.RUNNING
        self.spawn_fruit()

    def spawn_fruit(self) -> None:
        """Choose an unoccupied cell without recursion, even when full."""
        occupied = set(self.body)
        free = [
            (x, y)
            for y in range(self.rows)
            for x in range(self.columns)
            if (x, y) not in occupied
        ]
        if not free:
            self.fruit = None
            self.state = GameState.WON
        else:
            self.fruit = self.rng.choice(free)

    def request_direction(self, direction: Direction | str) -> bool:
        """Queue a legal turn; return False for reversals or a full queue."""
        if isinstance(direction, str):
            direction = Direction[direction.upper()]
        anchor = self._turns[-1] if self._turns else self.direction
        if (
            not self.alive
            or direction is anchor
            or direction is anchor.opposite
            or len(self._turns) >= 2
        ):
            return False
        self._turns.append(direction)
        return True

    def tick(self) -> bool:
        """Move one cell, grow on food, and detect walls and body collisions."""
        if not self.alive:
            return False
        if self._turns:
            self.direction = self._turns.popleft()
        dx, dy = self.direction.value
        x, y = self.head
        new_head = (x + dx, y + dy)
        eating = new_head == self.fruit
        # The tail leaves its cell during a non-growing move, so moving
        # into that cell is legal. It stays occupied when fruit is eaten.
        occupied = self.body if eating else self.body[:-1]
        if (
            not (0 <= new_head[0] < self.columns)
            or not (0 <= new_head[1] < self.rows)
            or new_head in occupied
        ):
            self.state = GameState.LOST
            self.collision_at = new_head
            self._turns.clear()
            return False
        self.body.insert(0, new_head)
        if eating:
            self.score += 1
            self.spawn_fruit()
        else:
            self.body.pop()
        return eating


_NAVY = (14, 23, 38)
_PANEL = (22, 36, 54)
_BOARD_A = (23, 43, 50)
_BOARD_B = (25, 46, 53)
_MINT = (120, 239, 181)
_GREEN = (70, 184, 132)
_DARK_GREEN = (34, 105, 85)
_GOLD = (255, 192, 86)
_WHITE = (234, 242, 245)
_MUTED = (143, 165, 179)
_RED = (249, 126, 123)


def _make_sounds(pygame: Any) -> dict[str, Any]:
    """Make small original PCM effects; the game also works without audio."""
    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
        sample_rate, sample_size, channels = pygame.mixer.get_init()
        if sample_size != -16:
            return {}
        sounds = {}
        notes = {
            "eat": ((660.0, 0.065), (880.0, 0.085)),
            "lose": ((260.0, 0.12), (190.0, 0.13), (130.0, 0.2)),
            "win": ((523.25, 0.1), (659.25, 0.1), (783.99, 0.18)),
        }
        for name, sequence in notes.items():
            samples = array("h")
            for frequency, seconds in sequence:
                count = int(sample_rate * seconds)
                for index in range(count):
                    envelope = min(1.0, index / max(1, sample_rate * 0.008))
                    envelope *= min(1.0, (count - index) / max(1, sample_rate * 0.03))
                    value = int(5000 * envelope * math.sin(2 * math.pi * frequency * index / sample_rate))
                    samples.extend([value] * channels)
            sounds[name] = pygame.mixer.Sound(buffer=samples.tobytes())
        return sounds
    except (pygame.error, TypeError, ValueError):
        return {}


def run(*, max_frames: int | None = None) -> None:
    """Open the game. Escape returns to the launcher; R/Enter restart.

    ``max_frames`` provides a bounded render smoke test with SDL's dummy
    driver. Normal play leaves this argument unset.
    """
    import pygame

    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    try:
        screen = pygame.display.set_mode((780, 810))
        pygame.display.set_caption("Pygame Camp | Snake")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("segoeui", 23)
        small_font = pygame.font.SysFont("segoeui", 17)
        title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        large_font = pygame.font.SysFont("segoeui", 48, bold=True)
        sounds = _make_sounds(pygame)
        model = SnakeGame()
        board = pygame.Rect(30, 120, 720, 630)
        ready = True
        paused = False
        muted = False
        best = 0
        elapsed = 0.0
        frame_count = 0
        running = True
        key_directions = {
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_d: Direction.RIGHT,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_s: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_a: Direction.LEFT,
            pygame.K_UP: Direction.UP,
            pygame.K_w: Direction.UP,
        }

        def text(message: str, position: tuple[int, int], *, color: tuple[int, int, int] = _WHITE,
                 selected_font: Any = font, anchor: str = "topleft") -> None:
            surface = selected_font.render(message, True, color)
            rectangle = surface.get_rect(**{anchor: position})
            screen.blit(surface, rectangle)

        def play(name: str) -> None:
            if not muted and name in sounds:
                sounds[name].play()

        def start_round() -> None:
            nonlocal ready, paused, elapsed
            model.reset()
            ready = False
            paused = False
            elapsed = 0.0

        def draw_board() -> None:
            pygame.draw.rect(screen, _DARK_GREEN, board.inflate(8, 8), border_radius=9)
            for row in range(model.rows):
                for column in range(model.columns):
                    color = _BOARD_A if (row + column) % 2 == 0 else _BOARD_B
                    pygame.draw.rect(screen, color, (board.x + column * 30, board.y + row * 30, 30, 30))
            if model.fruit is not None:
                fruit_x = board.x + model.fruit[0] * 30
                fruit_y = board.y + model.fruit[1] * 30
                pygame.draw.circle(screen, (183, 107, 40), (fruit_x + 15, fruit_y + 17), 12)
                pygame.draw.circle(screen, _GOLD, (fruit_x + 15, fruit_y + 15), 11)
                pygame.draw.line(screen, _DARK_GREEN, (fruit_x + 15, fruit_y + 6), (fruit_x + 17, fruit_y + 2), 3)
                pygame.draw.ellipse(screen, _MINT, (fruit_x + 17, fruit_y + 1, 8, 5))
                pygame.draw.circle(screen, (255, 222, 155), (fruit_x + 11, fruit_y + 11), 3)
            for index, (x, y) in reversed(list(enumerate(model.body))):
                rectangle = pygame.Rect(board.x + x * 30 + 1, board.y + y * 30 + 1, 28, 28)
                pygame.draw.rect(screen, _DARK_GREEN, rectangle, border_radius=7)
                pygame.draw.rect(screen, _MINT if index == 0 else _GREEN, rectangle.inflate(-4, -4), border_radius=5)
                if index == 0:
                    cx, cy = rectangle.center
                    dx, dy = model.direction.value
                    perpendicular = (-dy, dx)
                    for side in (-1, 1):
                        eye = (cx + dx * 6 + perpendicular[0] * side * 6,
                               cy + dy * 6 + perpendicular[1] * side * 6)
                        pygame.draw.circle(screen, _WHITE, eye, 4)
                        pygame.draw.circle(screen, _NAVY, (eye[0] + dx, eye[1] + dy), 2)

        def draw_overlay(heading: str, description: str, hint: str, color: tuple[int, int, int]) -> None:
            shade = pygame.Surface(board.size, pygame.SRCALPHA)
            shade.fill((9, 17, 29, 205))
            screen.blit(shade, board.topleft)
            card = pygame.Rect(135, 312, 510, 238)
            pygame.draw.rect(screen, _PANEL, card, border_radius=20)
            pygame.draw.rect(screen, (56, 77, 93), card, width=2, border_radius=20)
            text(heading, (390, 367), selected_font=large_font, anchor="center", color=color)
            text(description, (390, 427), anchor="center")
            text(hint, (390, 482), selected_font=small_font, anchor="center", color=_MUTED)

        while running and (max_frames is None or frame_count < max_frames):
            delta = min(clock.tick(60) / 1000.0, 0.1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.WINDOWFOCUSLOST and model.alive and not ready:
                    paused = True
                    elapsed = 0.0
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_m:
                        muted = not muted
                    elif event.key in (pygame.K_RETURN, pygame.K_r):
                        if ready or not model.alive or event.key == pygame.K_r:
                            start_round()
                    elif event.key in (pygame.K_SPACE, pygame.K_p):
                        if ready:
                            start_round()
                        elif model.alive:
                            paused = not paused
                            elapsed = 0.0
                    elif event.key in key_directions and not paused:
                        if ready:
                            start_round()
                        model.request_direction(key_directions[event.key])
            if not running:
                break
            if model.alive and not ready and not paused:
                elapsed += delta
                while elapsed >= 0.1 and model.alive:
                    elapsed -= 0.1
                    if model.tick():
                        best = max(best, model.score)
                        play("eat")
                    if model.state is GameState.LOST:
                        play("lose")
                    elif model.state is GameState.WON:
                        play("win")

            screen.fill(_NAVY)
            text("SNAKE", (30, 23), selected_font=title_font, color=_MINT)
            text("Eat. Grow. Keep moving.", (30, 72), selected_font=small_font, color=_MUTED)
            text(f"SCORE  {model.score:02d}", (750, 32), anchor="topright", color=_GOLD)
            text(f"BEST  {best:02d}", (750, 72), selected_font=small_font, anchor="topright", color=_MUTED)
            draw_board()
            if ready:
                draw_overlay("LET'S PLAY", "Eat fruit. Avoid walls and your own tail.",
                             "Enter or arrows / WASD to start", _MINT)
            elif paused:
                draw_overlay("PAUSED", "Take a breath. Your snake can wait.", "Space / P to continue", _GOLD)
            elif model.state is GameState.LOST:
                draw_overlay("GAME OVER", f"You ate {model.score} fruit. Best this session: {best}.",
                             "Enter / R to try again     Esc for menu", _RED)
            elif model.state is GameState.WON:
                draw_overlay("YOU WIN!", "Every square is yours. Perfect run!", "Enter / R for a new round", _MINT)
            text("Arrows / WASD: move    Space: pause    R: restart    Esc: menu", (30, 769),
                 selected_font=small_font, color=_MUTED)
            text("M: " + ("muted" if muted else "sound"), (750, 769), selected_font=small_font,
                 anchor="topright", color=_MUTED)
            pygame.display.flip()
            frame_count += 1
    finally:
        pygame.quit()


if __name__ == "__main__":
    run()
