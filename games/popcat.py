"""A small Popcat game inspired by the camp's mouse-event lesson.

The cat art is drawn with Pygame and the pop sound is synthesized locally.
There are no image, font, or sound files to download.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass, field
import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame


@dataclass
class PopcatState:
    """Count presses while keeping the mouth open until all inputs release."""

    clicks: int = 0
    _held_inputs: set[str] = field(default_factory=set, repr=False)

    @property
    def mouth_open(self) -> bool:
        return bool(self._held_inputs)

    def press(self, input_id: str = "mouse") -> bool:
        """Register a fresh press; repeated key-down events do not add points."""
        if input_id in self._held_inputs:
            return False
        self._held_inputs.add(input_id)
        self.clicks += 1
        return True

    def release(self, input_id: str = "mouse") -> None:
        self._held_inputs.discard(input_id)

    def release_all(self) -> None:
        self._held_inputs.clear()

    def reset(self) -> None:
        self.clicks = 0
        self.release_all()


BACKGROUND = (20, 29, 48)
PANEL = (31, 43, 66)
TEXT = (250, 243, 230)
MUTED = (157, 174, 197)
GOLD = (247, 197, 112)
PEACH = (244, 154, 130)
INK = (49, 39, 49)
SIZE = (900, 640)


@dataclass
class _Cat:
    state: PopcatState
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    pulse: float = 0.0


def _make_cat_surface(mouth_open: bool, accent: tuple[int, int, int]) -> pygame.Surface:
    import pygame

    # Draw at twice the final size for smooth vector edges.
    surface = pygame.Surface((600, 620), pygame.SRCALPHA)
    cream = (244, 222, 186)
    light = (255, 239, 212)
    shade = (204, 168, 131)

    pygame.draw.ellipse(surface, (0, 0, 0, 45), (92, 529, 416, 60))
    pygame.draw.ellipse(surface, shade, (110, 398, 380, 176))
    pygame.draw.ellipse(surface, cream, (126, 386, 348, 172))
    pygame.draw.ellipse(surface, light, (224, 438, 152, 118))

    # Ears and face are one original illustrated character.
    pygame.draw.polygon(surface, INK, [(84, 254), (80, 49), (240, 141)])
    pygame.draw.polygon(surface, INK, [(360, 141), (520, 49), (516, 254)])
    pygame.draw.polygon(surface, cream, [(97, 248), (94, 74), (229, 153)])
    pygame.draw.polygon(surface, cream, [(371, 153), (506, 74), (503, 248)])
    pygame.draw.polygon(surface, accent, [(116, 213), (112, 114), (203, 169)])
    pygame.draw.polygon(surface, accent, [(397, 169), (488, 114), (484, 213)])
    pygame.draw.ellipse(surface, INK, (60, 116, 480, 372))
    pygame.draw.ellipse(surface, cream, (69, 124, 462, 356))
    pygame.draw.ellipse(surface, light, (141, 255, 318, 208))

    # Forehead stripes give the cat a recognizable tabby silhouette.
    pygame.draw.polygon(surface, shade, [(235, 136), (264, 133), (259, 186)])
    pygame.draw.polygon(surface, shade, [(283, 128), (317, 128), (300, 191)])
    pygame.draw.polygon(surface, shade, [(336, 133), (365, 136), (341, 186)])

    pygame.draw.ellipse(surface, INK, (155, 230, 38, 55))
    pygame.draw.ellipse(surface, INK, (407, 230, 38, 55))
    pygame.draw.ellipse(surface, TEXT, (164, 236, 11, 14))
    pygame.draw.ellipse(surface, TEXT, (416, 236, 11, 14))
    pygame.draw.ellipse(surface, accent, (116, 300, 62, 25))
    pygame.draw.ellipse(surface, accent, (422, 300, 62, 25))
    pygame.draw.polygon(surface, INK, [(278, 295), (322, 295), (300, 316)])
    pygame.draw.polygon(surface, accent, [(285, 297), (315, 297), (300, 309)])

    if mouth_open:
        pygame.draw.ellipse(surface, INK, (231, 324, 138, 131))
        pygame.draw.ellipse(surface, (91, 49, 61), (242, 334, 116, 108))
        pygame.draw.ellipse(surface, accent, (263, 396, 74, 43))
        pygame.draw.ellipse(surface, (250, 200, 174), (273, 400, 46, 15))
    else:
        pygame.draw.line(surface, INK, (300, 312), (300, 329), 7)
        pygame.draw.arc(surface, INK, (254, 303, 48, 47), math.pi, 2 * math.pi, 7)
        pygame.draw.arc(surface, INK, (298, 303, 48, 47), math.pi, 2 * math.pi, 7)

    for side in (-1, 1):
        for y, slope in ((322, -12), (348, 0), (374, 12)):
            start = (300 + side * 142, y)
            end = (300 + side * 242, y + slope)
            pygame.draw.line(surface, INK, start, end, 5)

    pygame.draw.ellipse(surface, shade, (160, 516, 91, 48))
    pygame.draw.ellipse(surface, shade, (349, 516, 91, 48))
    pygame.draw.ellipse(surface, cream, (160, 508, 91, 48))
    pygame.draw.ellipse(surface, cream, (349, 508, 91, 48))
    return pygame.transform.smoothscale(surface, (300, 310))


def _make_pop_sound() -> pygame.mixer.Sound | None:
    import pygame

    if pygame.mixer.get_init() is None:
        return None
    sample_rate, sample_format, channels = pygame.mixer.get_init()
    if sample_format != -16:
        return None
    samples = array("h")
    length = int(sample_rate * 0.095)
    for index in range(length):
        time = index / sample_rate
        # A quick downward chirp with an exponential envelope makes a soft pop.
        phase = 2 * math.pi * (620 * time - 2400 * time * time)
        attack = min(1.0, index / max(1, int(sample_rate * 0.003)))
        amplitude = int(17000 * attack * math.exp(-time * 42) * math.sin(phase))
        samples.extend([amplitude] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    content: str,
    center: tuple[int, int],
    color: tuple[int, int, int] = TEXT,
) -> None:
    rendered = font.render(content, True, color)
    screen.blit(rendered, rendered.get_rect(center=center))


def run(*, max_frames: int | None = None) -> None:
    """Play until close/Escape, or render a bounded number of frames for checks."""
    import pygame

    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    try:
        screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption("Pygame Camp | Popcat")
        clock = pygame.time.Clock()
        font_small = pygame.font.Font(None, 24)
        font_label = pygame.font.Font(None, 28)
        font_title = pygame.font.Font(None, 60)
        font_score = pygame.font.Font(None, 64)
        sound = _make_pop_sound()
        sprites = [
            (_make_cat_surface(False, PEACH), _make_cat_surface(True, PEACH)),
            (_make_cat_surface(False, GOLD), _make_cat_surface(True, GOLD)),
        ]
        cats = [_Cat(PopcatState(), 450, 344), _Cat(PopcatState(), 630, 370)]
        moving = False
        muted = False
        active_mouse: int | None = None
        frames = 0
        rng = random.Random()

        def pop(cat_index: int, input_id: str) -> None:
            cat = cats[cat_index]
            if cat.state.press(input_id):
                cat.pulse = 1.0
                if sound is not None and not muted:
                    sound.play()

        def reset() -> None:
            nonlocal active_mouse
            active_mouse = None
            for cat in cats:
                cat.state.reset()
                cat.pulse = 0.0
            if moving:
                cats[0].x, cats[0].y = 270, 335
                cats[1].x, cats[1].y = 630, 350
                for index, cat in enumerate(cats):
                    cat.vx = 65.0 if index == 0 else -65.0
                    cat.vy = rng.choice((-35.0, 35.0))
            else:
                cats[0].x, cats[0].y = 450, 344
                cats[0].vx = cats[0].vy = 0.0

        running = True
        while running and (max_frames is None or frames < max_frames):
            dt = min(clock.tick(60) / 1000.0, 0.05)
            visible_cats = cats if moving else cats[:1]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        pop(0, f"key:{event.key}")
                    elif event.key == pygame.K_r:
                        reset()
                    elif event.key == pygame.K_TAB:
                        moving = not moving
                        reset()
                    elif event.key == pygame.K_m:
                        muted = not muted
                elif event.type == pygame.KEYUP:
                    for cat in cats:
                        cat.state.release(f"key:{event.key}")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # The topmost cat gets the click if the moving cats overlap.
                    for index in reversed(range(2 if moving else 1)):
                        cat = cats[index]
                        rect = sprites[index][0].get_rect(center=(round(cat.x), round(cat.y)))
                        if rect.collidepoint(event.pos) and sprites[index][0].get_at(
                            (event.pos[0] - rect.x, event.pos[1] - rect.y)
                        ).a > 50:
                            active_mouse = index
                            pop(index, "mouse")
                            break
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if active_mouse is not None:
                        cats[active_mouse].state.release("mouse")
                    active_mouse = None
                elif event.type == pygame.WINDOWFOCUSLOST:
                    # Avoid a stuck-open mouth when a release occurs in another app.
                    for cat in cats:
                        cat.state.release_all()
                    active_mouse = None

            # Re-evaluate immediately after Tab, before drawing or hit testing.
            visible_cats = cats if moving else cats[:1]
            for cat in visible_cats:
                cat.pulse = max(0.0, cat.pulse - dt * 4)
                if moving:
                    cat.x += cat.vx * dt
                    cat.y += cat.vy * dt
                    if cat.x < 165 or cat.x > 735:
                        cat.x = min(735, max(165, cat.x))
                        cat.vx *= -1
                    if cat.y < 300 or cat.y > 385:
                        cat.y = min(385, max(300, cat.y))
                        cat.vy *= -1

            screen.fill(BACKGROUND)
            pygame.draw.rect(screen, PANEL, (24, 22, 852, 108), border_radius=24)
            title = font_title.render("POPCAT", True, TEXT)
            screen.blit(title, (47, 35))
            subtitle = font_small.render("Click. Hold. Pop!", True, MUTED)
            screen.blit(subtitle, (50, 93))
            total = sum(cat.state.clicks for cat in visible_cats)
            _text(screen, font_score, str(total), (762, 67), GOLD)
            _text(screen, font_small, "TOTAL POPS", (762, 105), MUTED)

            mode = "TWO MOVING CATS" if moving else "ONE HAPPY CAT"
            _text(screen, font_small, mode, (450, 154), MUTED)
            for index, cat in enumerate(visible_cats):
                if cat.pulse > 0:
                    radius = round(135 + (1 - cat.pulse) * 38)
                    ring = pygame.Surface(SIZE, pygame.SRCALPHA)
                    pygame.draw.circle(
                        ring,
                        (*((PEACH, GOLD)[index]), round(cat.pulse * 100)),
                        (round(cat.x), round(cat.y)),
                        radius,
                        3,
                    )
                    screen.blit(ring, (0, 0))
                sprite = sprites[index][int(cat.state.mouth_open)]
                scale = 1.0 + cat.pulse * 0.035
                if scale > 1.001:
                    sprite = pygame.transform.smoothscale(
                        sprite, (round(300 * scale), round(310 * scale))
                    )
                screen.blit(sprite, sprite.get_rect(center=(round(cat.x), round(cat.y))))
                if moving:
                    _text(screen, font_label, str(cat.state.clicks), (round(cat.x), round(cat.y + 152)), GOLD)

            pygame.draw.rect(screen, PANEL, (24, 545, 852, 72), border_radius=20)
            _text(screen, font_label, "LEFT CLICK / SPACE / ENTER  -  POP", (450, 567))
            _text(
                screen,
                font_small,
                "TAB  -  CHANGE MODE    R  -  RESET    M  -  SOUND    ESC  -  BACK",
                (450, 593),
                MUTED,
            )
            audio_status = "MUTED" if muted else ("SOUND ON" if sound is not None else "SOUND UNAVAILABLE")
            _text(screen, font_small, audio_status, (773, 154), MUTED)
            pygame.display.flip()
            frames += 1
    finally:
        pygame.quit()


if __name__ == "__main__":
    run()
