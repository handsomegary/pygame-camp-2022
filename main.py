"""Launch the camp games or the optional class design demonstration."""

from __future__ import annotations

import argparse
import importlib
import os
import sys


def load_pygame():
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    try:
        import pygame
    except ModuleNotFoundError as error:
        if error.name != "pygame":
            raise
        print("Pygame is missing. Install it with:\n  python -m pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(1) from error
    return pygame


def choose_game(pygame) -> str | None:
    """Return a game name; closing the menu returns None."""
    pygame.init()
    try:
        screen = pygame.display.set_mode((860, 640))
        pygame.display.set_caption("2022 Pygame Camp | Game collection")
        clock = pygame.time.Clock()
        title = pygame.font.Font(None, 66)
        heading = pygame.font.Font(None, 38)
        text = pygame.font.Font(None, 27)
        small = pygame.font.Font(None, 23)
        cards = [("popcat", pygame.Rect(50, 250, 365, 220)), ("snake", pygame.Rect(445, 250, 365, 220))]
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        return "popcat"
                    if event.key in (pygame.K_2, pygame.K_KP2):
                        return "snake"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for name, rect in cards:
                        if rect.collidepoint(event.pos):
                            return name
            screen.fill((18, 25, 43))
            screen.blit(small.render("PYGAME / BUILD PLAYABLE GAMES", True, (132, 153, 183)), (52, 58))
            screen.blit(title.render("Pygame Camp", True, (245, 242, 233)), (48, 98))
            screen.blit(text.render("Two games. Practical Pygame notes.", True, (163, 177, 198)), (52, 171))
            pointer = pygame.mouse.get_pos()
            for name, rect in cards:
                hovered = rect.collidepoint(pointer)
                color = (43, 57, 79) if hovered else (29, 40, 59)
                accent = (255, 187, 142) if name == "popcat" else (128, 222, 175)
                pygame.draw.rect(screen, color, rect, border_radius=22)
                pygame.draw.rect(screen, accent if hovered else (57, 74, 98), rect, 2, border_radius=22)
                x, y = rect.x + 25, rect.y + 24
                if name == "popcat":
                    pygame.draw.polygon(screen, accent, [(x, y + 25), (x + 5, y), (x + 24, y + 19)])
                    pygame.draw.polygon(screen, accent, [(x + 38, y + 19), (x + 58, y), (x + 62, y + 25)])
                    pygame.draw.ellipse(screen, accent, (x, y + 12, 63, 49))
                    pygame.draw.circle(screen, color, (x + 19, y + 32), 3)
                    pygame.draw.circle(screen, color, (x + 44, y + 32), 3)
                    pygame.draw.ellipse(screen, color, (x + 25, y + 39, 13, 15))
                    label, lines = "1 / POPCAT", ("Click, pop, repeat.", "Try the two moving cats challenge.")
                else:
                    for dx, dy in ((0, 0), (0, 23), (23, 23), (46, 23)):
                        pygame.draw.rect(screen, accent, (x + dx, y + dy + 8, 22, 22), border_radius=6)
                    pygame.draw.circle(screen, color, (x + 7, y + 14), 2)
                    pygame.draw.circle(screen, (255, 184, 102), (x + 89, y + 20), 10)
                    label, lines = "2 / SNAKE", ("Eat fruit. Keep growing.", "Avoid the walls and your own tail.")
                screen.blit(heading.render(label, True, accent), (x, y + 85))
                for index, line in enumerate(lines):
                    screen.blit(small.render(line, True, (192, 204, 221)), (x, y + 134 + index * 27))
            screen.blit(text.render("Click a card or press 1 / 2 to play.", True, (192, 204, 221)), (52, 519))
            screen.blit(small.render("Esc returns here from a game. Esc here closes the app.", True, (132, 153, 183)), (52, 558))
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--game", choices=("popcat", "snake"), help="start one game directly")
    group.add_argument("--example", choices=("classes",), help="run the class design demonstration without Pygame")
    group.add_argument("--smoke-test", action="store_true", help="briefly render both games without a window")
    args = parser.parse_args(argv)
    if args.example:
        importlib.import_module(f"examples.{args.example}").main()
        return 0
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    pygame = load_pygame()
    if args.smoke_test:
        for name in ("popcat", "snake"):
            importlib.import_module(f"games.{name}").run(max_frames=3)
            print(f"{name}: rendered successfully")
        return 0
    if args.game:
        importlib.import_module(f"games.{args.game}").run()
        return 0
    while (name := choose_game(pygame)) is not None:
        importlib.import_module(f"games.{name}").run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
