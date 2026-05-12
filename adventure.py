"""
Atari Adventure Homage — game loop and render foundation.

Constants
---------
LOGICAL_W  : int  — logical canvas width in pixels  (160)
LOGICAL_H  : int  — logical canvas height in pixels (210)
SCALE      : int  — default window scale factor     (3 → 480×630 display)
"""

import sys
import os

import pygame

# ---------------------------------------------------------------------------
# Display constants
# ---------------------------------------------------------------------------
LOGICAL_W: int = 160
LOGICAL_H: int = 210
SCALE: int = 3

# Room layout constants
WALL_THICKNESS: int = 8          # pixels
BACKGROUND_COLOR = (0, 0, 0)    # black interior
WALL_COLOR = (255, 255, 0)       # yellow walls

# Player constants
PLAYER_SIZE: int = 8             # player is a square: 8x8 pixels
PLAYER_START_X: int = LOGICAL_W // 2 - PLAYER_SIZE // 2   # near center horizontally
PLAYER_START_Y: int = LOGICAL_H // 2 - PLAYER_SIZE // 2   # near center vertically


# ---------------------------------------------------------------------------
# IGameInitializer contract
# ---------------------------------------------------------------------------

def initialize() -> tuple[int, int]:
    """
    Initialise all pygame subsystems.

    Returns
    -------
    (success_count, fail_count) : tuple[int, int]
        The values returned directly by pygame.init().
        fail_count must be 0 for the game to function correctly.
    """
    return pygame.init()


def set_display_mode(
    logical_w: int = LOGICAL_W,
    logical_h: int = LOGICAL_H,
    scale: int = SCALE,
) -> pygame.Surface:
    """
    Create the display surface at logical_w*scale × logical_h*scale pixels.

    Parameters
    ----------
    logical_w : int  — logical canvas width  (default LOGICAL_W=160)
    logical_h : int  — logical canvas height (default LOGICAL_H=210)
    scale     : int  — integer scale factor  (default SCALE=3)

    Returns
    -------
    pygame.Surface
        The display surface created by pygame.display.set_mode().
    """
    window_w = logical_w * scale
    window_h = logical_h * scale
    surface = pygame.display.set_mode((window_w, window_h))
    pygame.display.set_caption("Adventure")
    return surface


def shutdown() -> None:
    """Shut down all pygame subsystems cleanly."""
    pygame.quit()


# ---------------------------------------------------------------------------
# Rendering functions
# ---------------------------------------------------------------------------

def draw_background(surface: pygame.Surface) -> None:
    """Fill the inner area (inside walls) with BACKGROUND_COLOR."""
    inner_rect = pygame.Rect(
        WALL_THICKNESS, WALL_THICKNESS,
        LOGICAL_W - 2 * WALL_THICKNESS,
        LOGICAL_H - 2 * WALL_THICKNESS,
    )
    pygame.draw.rect(surface, BACKGROUND_COLOR, inner_rect)


def draw_walls(surface: pygame.Surface) -> None:
    """Draw 4 wall rects: top, bottom, left, right."""
    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, LOGICAL_W, WALL_THICKNESS))                              # top
    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, LOGICAL_H - WALL_THICKNESS, LOGICAL_W, WALL_THICKNESS))    # bottom
    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, WALL_THICKNESS, LOGICAL_H))                              # left
    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(LOGICAL_W - WALL_THICKNESS, 0, WALL_THICKNESS, LOGICAL_H))    # right


def draw_player(surface: pygame.Surface, x: int = PLAYER_START_X, y: int = PLAYER_START_Y) -> None:
    """Draw the player square at the given coordinates."""
    player_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
    pygame.draw.rect(surface, (255, 255, 255), player_rect)  # white player


# Player coordinate aliases expected by tests
PLAYER_X: int = PLAYER_START_X
PLAYER_Y: int = PLAYER_START_Y


# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------

def run_game_loop(screen: pygame.Surface | None = None) -> None:
    """
    Run the main game loop until a QUIT or ESC event is received.

    Parameters
    ----------
    screen : pygame.Surface | None
        The display surface to render to.  If None the loop still processes
        events (useful for headless / test runs).
    """
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
        if screen is not None:
            draw_background(screen)
            draw_walls(screen)
            draw_player(screen)
            pygame.display.flip()
        clock.tick(30)
    pygame.quit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Initialise pygame, create the window, run the game loop, then exit cleanly.
    """
    success_count, fail_count = initialize()
    if fail_count != 0:
        print(f"Warning: pygame.init() reported {fail_count} subsystem failure(s).", file=sys.stderr)
    screen = set_display_mode()
    pygame.display.set_caption("Adventure")
    run_game_loop(screen)


if __name__ == "__main__":
    main()
