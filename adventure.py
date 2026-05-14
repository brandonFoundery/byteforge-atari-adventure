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

# Item constants (T4)
CHALICE_X = 40
CHALICE_Y = 50
CHALICE_COLOR = (255, 215, 0)    # gold

KEY_X = 100
KEY_Y = 80
KEY_COLOR = (192, 192, 192)      # silver

SWORD_X = 70
SWORD_Y = 140
SWORD_COLOR = (200, 200, 200)    # light grey

ITEM_SIZE = 6

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


def _init_items() -> list:
    """Return a fresh list of item dicts for a new game session."""
    return [
        {"kind": "chalice", "x": CHALICE_X, "y": CHALICE_Y, "size": ITEM_SIZE, "color": CHALICE_COLOR},
        {"kind": "key",     "x": KEY_X,     "y": KEY_Y,     "size": ITEM_SIZE, "color": KEY_COLOR},
        {"kind": "sword",   "x": SWORD_X,   "y": SWORD_Y,   "size": ITEM_SIZE, "color": SWORD_COLOR},
    ]


def _init_carried():
    """Return None — no item carried at game start."""
    return None


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


def _try_pickup(px: int, py: int, player_size: int, floor_items: list, carried):
    """AABB pickup check: if not carrying and player overlaps an item, pick it up.

    Returns (floor_items, carried) where floor_items has the picked-up item
    removed and carried is set to that item.  If already carrying, returns
    inputs unchanged.
    """
    if carried is not None:
        return floor_items, carried
    for item in floor_items:
        if (px < item['x'] + item['size'] and px + player_size > item['x'] and
                py < item['y'] + item['size'] and py + player_size > item['y']):
            new_floor = [i for i in floor_items if i is not item]
            return new_floor, item
    return floor_items, carried


def _on_drop_key(px: int, py: int, floor_items: list, carried):
    """Edge-triggered drop: place carried item at (px, py) and clear carried slot.

    Returns (floor_items, carried).  If carried is None this is a no-op.
    """
    if carried is None:
        return floor_items, None
    dropped = dict(carried)
    dropped['x'] = px
    dropped['y'] = py
    return floor_items + [dropped], None


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


def draw_items(surface: pygame.Surface, floor_items: list, carried, px: int, py: int) -> None:
    """Render floor items and the carried item (offset from player)."""
    for item in floor_items:
        pygame.draw.rect(surface, item['color'], pygame.Rect(item['x'], item['y'], item['size'], item['size']))
    if carried is not None:
        pygame.draw.rect(surface, carried['color'], pygame.Rect(px + PLAYER_SIZE, py, carried['size'], carried['size']))


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
    items = _init_items()
    carried = _init_carried()

    while running:
        for event in event_getter():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                items, carried = _on_drop_key(px, py, items, carried)

        px, py = move_player(px, py, pygame.key.get_pressed())
        items, carried = _try_pickup(px, py, PLAYER_SIZE, items, carried)

        draw_room(logical_surface)
        draw_items(logical_surface, items, carried, px, py)
        draw_player(logical_surface, px, py)

        if surface.get_size() == (LOGICAL_WIDTH, LOGICAL_HEIGHT):
            surface.blit(logical_surface, (0, 0))
        else:
            pygame.transform.scale(logical_surface, surface.get_size(), surface)
        if pygame.display.get_surface() is not None:
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
