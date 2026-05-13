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


def move_player(x: int, y: int, keys_pressed) -> tuple[int, int]:
    """Apply arrow-key movement and clamp to room interior."""
    if keys_pressed[pygame.K_RIGHT]:
        x += PLAYER_SPEED
    if keys_pressed[pygame.K_LEFT]:
        x -= PLAYER_SPEED
    if keys_pressed[pygame.K_DOWN]:
        y += PLAYER_SPEED
    if keys_pressed[pygame.K_UP]:
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
