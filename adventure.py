"""Atari Adventure homage (T1): game loop + single-room render foundation."""

from __future__ import annotations

import pygame

LOGICAL_WIDTH = 160
LOGICAL_HEIGHT = 210
WINDOW_SCALE = 3
TARGET_FPS = 30

WALL_THICKNESS = 8
ROOM_COLOR = (240, 208, 64)   # gold-like castle room
WALL_COLOR = (32, 32, 32)
PLAYER_COLOR = (200, 32, 32)
PLAYER_SIZE = 8

PLAYER_X = (LOGICAL_WIDTH - PLAYER_SIZE) // 2
PLAYER_Y = (LOGICAL_HEIGHT - PLAYER_SIZE) // 2

PLAYER_SPEED = 2

_X_MIN = WALL_THICKNESS
_X_MAX = LOGICAL_WIDTH - WALL_THICKNESS - PLAYER_SIZE
_Y_MIN = WALL_THICKNESS
_Y_MAX = LOGICAL_HEIGHT - WALL_THICKNESS - PLAYER_SIZE

# Legacy SDL1 key constants (used by test fixtures that don't import pygame).
# These numeric values mirror the classic SDLK_* definitions.
_K_UP = 273
_K_DOWN = 274
_K_RIGHT = 275
_K_LEFT = 276


def _is_pressed(keys_pressed, sdl1_val: int, sdl2_val: int) -> bool:
    """Return True when the key is pressed.

    Supports three styles of ``keys_pressed``:
    * ``pygame.key.get_pressed()`` sequence — indexed by SDL2 scancode.
    * A dict keyed by SDL2 constants (e.g. ``{pygame.K_RIGHT: True}``).
    * A dict keyed by SDL1 constants (e.g. ``{275: True}``).
    """
    try:
        # dict.get works for both SDL1 and SDL2 keyed dicts
        v1 = keys_pressed.get(sdl1_val, False)
        v2 = keys_pressed.get(sdl2_val, False)
        return bool(v1 or v2)
    except AttributeError:
        # pygame.key.get_pressed() returns a sequence; index by SDL2 value
        return bool(keys_pressed[sdl2_val])


def move_player(x: int, y: int, keys_pressed) -> tuple[int, int]:
    """Apply arrow-key movement and clamp to room interior."""
    if _is_pressed(keys_pressed, _K_RIGHT, pygame.K_RIGHT):
        x += PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_LEFT, pygame.K_LEFT):
        x -= PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_DOWN, pygame.K_DOWN):
        y += PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_UP, pygame.K_UP):
        y -= PLAYER_SPEED
    return max(_X_MIN, min(_X_MAX, x)), max(_Y_MIN, min(_Y_MAX, y))


def initialize_pygame() -> tuple[int, int]:
    """Initialize pygame subsystems."""
    return pygame.init()


def create_window(scale: int = WINDOW_SCALE) -> pygame.Surface:
    """Create the scaled window surface."""
    return pygame.display.set_mode((LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale))


def draw_room(surface: pygame.Surface) -> None:
    """Render the fixed room background and perimeter walls."""
    surface.fill(ROOM_COLOR)

    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, LOGICAL_WIDTH, WALL_THICKNESS))
    pygame.draw.rect(
        surface,
        WALL_COLOR,
        pygame.Rect(0, LOGICAL_HEIGHT - WALL_THICKNESS, LOGICAL_WIDTH, WALL_THICKNESS),
    )
    pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, WALL_THICKNESS, LOGICAL_HEIGHT))
    pygame.draw.rect(
        surface,
        WALL_COLOR,
        pygame.Rect(LOGICAL_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, LOGICAL_HEIGHT),
    )


def draw_player(surface: pygame.Surface, x: int = PLAYER_X, y: int = PLAYER_Y) -> None:
    """Render the player avatar as a small square."""
    pygame.draw.rect(surface, PLAYER_COLOR, pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE))


def run_game_loop(
    surface: pygame.Surface,
    *,
    fps: int = TARGET_FPS,
    event_getter=pygame.event.get,
) -> None:
    """Run until quit event or ESC key is received."""
    clock = pygame.time.Clock()
    running = True
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    px, py = PLAYER_X, PLAYER_Y

    while running:
        for event in event_getter():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        px, py = move_player(px, py, pygame.key.get_pressed())

        draw_room(logical_surface)
        draw_player(logical_surface, px, py)

        if surface.get_size() == (LOGICAL_WIDTH, LOGICAL_HEIGHT):
            surface.blit(logical_surface, (0, 0))
        else:
            pygame.transform.scale(logical_surface, surface.get_size(), surface)
        pygame.display.flip()
        clock.tick(fps)


def main() -> None:
    """Program entrypoint."""
    initialize_pygame()
    surface = create_window()
    pygame.display.set_caption("Adventure")

    try:
        run_game_loop(surface)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
