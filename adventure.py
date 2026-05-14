"""Atari Adventure homage (T1-T3): multi-room world with screen transitions."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

LOGICAL_WIDTH = 160
LOGICAL_HEIGHT = 210
WINDOW_SCALE = 3
TARGET_FPS = 30

WALL_THICKNESS = 8
ROOM_COLOR = (240, 208, 64)   # gold-like castle room (preserved alias)
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
_K_UP = 273
_K_DOWN = 274
_K_RIGHT = 275
_K_LEFT = 276


@dataclass(frozen=True)
class Room:
    id: str
    bg_color: tuple[int, int, int]
    neighbors: dict[str, str | None]


ROOMS: dict[str, Room] = {
    "yellow": Room("yellow", (240, 208, 64), {"N": None,     "S": "blue",   "E": "green",  "W": None}),
    "blue":   Room("blue",   (64, 96, 200),  {"N": "yellow", "S": None,     "E": "purple", "W": None}),
    "green":  Room("green",  (48, 160, 64),  {"N": None,     "S": "purple", "E": None,     "W": "yellow"}),
    "purple": Room("purple", (144, 64, 176), {"N": "green",  "S": None,     "E": None,     "W": "blue"}),
}

START_ROOM = "yellow"

OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

INWARD_OFFSET = PLAYER_SPEED + 1


def assert_symmetric(rooms: dict[str, Room]) -> None:
    """Verify every passage edge is bidirectional. Raises ValueError on violation."""
    for room_id, room in rooms.items():
        for direction, neighbor_id in room.neighbors.items():
            if neighbor_id is None:
                continue
            if neighbor_id not in rooms:
                raise ValueError(
                    f"Room {room_id!r} edge {direction!r} points to unknown room {neighbor_id!r}"
                )
            back = rooms[neighbor_id].neighbors.get(OPPOSITE[direction])
            if back != room_id:
                raise ValueError(
                    f"Asymmetric edge: {room_id!r}.{direction} -> "
                    f"{neighbor_id!r}, but {neighbor_id!r}.{OPPOSITE[direction]} -> {back!r}"
                )


def assert_connected(rooms: dict[str, Room], start: str) -> None:
    """Verify BFS from start reaches every room. Raises ValueError on disconnected graph."""
    visited: set[str] = set()
    queue = [start]
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        for neighbor_id in rooms[current].neighbors.values():
            if neighbor_id is not None and neighbor_id not in visited:
                queue.append(neighbor_id)
    missing = set(rooms) - visited
    if missing:
        raise ValueError(f"Rooms not reachable from {start!r}: {missing}")


def _is_pressed(keys_pressed, sdl1_val: int, sdl2_val: int) -> bool:
    """Return True when the key is pressed.

    Supports three styles of ``keys_pressed``:
    * ``pygame.key.get_pressed()`` sequence — indexed by SDL2 scancode.
    * A dict keyed by SDL2 constants (e.g. ``{pygame.K_RIGHT: True}``).
    * A dict keyed by SDL1 constants (e.g. ``{275: True}``).
    """
    try:
        v1 = keys_pressed.get(sdl1_val, False)
        v2 = keys_pressed.get(sdl2_val, False)
        return bool(v1 or v2)
    except AttributeError:
        return bool(keys_pressed[sdl2_val])


def move_player(
    x: int, y: int, keys_pressed, room: Room | None = None
) -> tuple[int, int] | tuple[str, str]:
    """Apply arrow-key movement.

    Legacy mode (room=None): clamp to room interior, return (x, y).
    Room-aware mode (room=Room): return ("exit", dir) on passage crossing,
    clamp on sealed edges, return (x, y) otherwise.
    Diagonal tie-break: horizontal axis checked first.
    """
    nx, ny = x, y
    if _is_pressed(keys_pressed, _K_RIGHT, pygame.K_RIGHT):
        nx += PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_LEFT, pygame.K_LEFT):
        nx -= PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_DOWN, pygame.K_DOWN):
        ny += PLAYER_SPEED
    if _is_pressed(keys_pressed, _K_UP, pygame.K_UP):
        ny -= PLAYER_SPEED

    if room is None:
        return max(_X_MIN, min(_X_MAX, nx)), max(_Y_MIN, min(_Y_MAX, ny))

    # Room-aware mode — horizontal axis first for deterministic diagonal policy
    if nx > _X_MAX:
        if room.neighbors["E"] is not None:
            return ("exit", "E")
        nx = _X_MAX
    elif nx < _X_MIN:
        if room.neighbors["W"] is not None:
            return ("exit", "W")
        nx = _X_MIN

    if ny > _Y_MAX:
        if room.neighbors["S"] is not None:
            return ("exit", "S")
        ny = _Y_MAX
    elif ny < _Y_MIN:
        if room.neighbors["N"] is not None:
            return ("exit", "N")
        ny = _Y_MIN

    return nx, ny


def _clamp_x(v: int) -> int:
    return max(_X_MIN, min(_X_MAX, v))


def _clamp_y(v: int) -> int:
    return max(_Y_MIN, min(_Y_MAX, v))


def _warp_position(room: Room, exit_dir: str, x: int, y: int) -> tuple[Room, int, int]:
    """Compute destination room and in-room coordinates after a passage exit.

    Pure function — no pygame dependency, no module-global writes.
    Raises ValueError for sealed edges, unknown rooms, or invalid directions.
    """
    neighbor_id = room.neighbors.get(exit_dir)
    if neighbor_id is None:
        raise ValueError(f"Cannot warp through sealed edge {room.id}.{exit_dir}")
    if neighbor_id not in ROOMS:
        raise ValueError(f"Unknown room id {neighbor_id!r} from {room.id}.{exit_dir}")
    new_room = ROOMS[neighbor_id]
    if exit_dir == "E":
        return new_room, _X_MIN + INWARD_OFFSET, _clamp_y(y)
    if exit_dir == "W":
        return new_room, _X_MAX - INWARD_OFFSET, _clamp_y(y)
    if exit_dir == "N":
        return new_room, _clamp_x(x), _Y_MAX - INWARD_OFFSET
    if exit_dir == "S":
        return new_room, _clamp_x(x), _Y_MIN + INWARD_OFFSET
    raise ValueError(f"Unknown exit direction: {exit_dir!r}")


def initialize_pygame() -> tuple[int, int]:
    """Initialize pygame subsystems."""
    return pygame.init()


def create_window(scale: int = WINDOW_SCALE) -> pygame.Surface:
    """Create the scaled window surface."""
    return pygame.display.set_mode((LOGICAL_WIDTH * scale, LOGICAL_HEIGHT * scale))


_LEGACY_ROOM = Room("_legacy", ROOM_COLOR, {"N": None, "S": None, "E": None, "W": None})


def draw_room(surface: pygame.Surface, room: Room | None = None) -> None:
    """Render the active room's background and walls.

    Walls are drawn ONLY on edges where room.neighbors[dir] is None (sealed).
    Passage edges show the bg color through.
    T1/T2 callers may omit room; _LEGACY_ROOM (all-walls, ROOM_COLOR) is used.
    """
    if room is None:
        room = _LEGACY_ROOM
    surface.fill(room.bg_color)

    if room.neighbors.get("N") is None:
        pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, LOGICAL_WIDTH, WALL_THICKNESS))
    if room.neighbors.get("S") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
            pygame.Rect(0, LOGICAL_HEIGHT - WALL_THICKNESS, LOGICAL_WIDTH, WALL_THICKNESS),
        )
    if room.neighbors.get("W") is None:
        pygame.draw.rect(surface, WALL_COLOR, pygame.Rect(0, 0, WALL_THICKNESS, LOGICAL_HEIGHT))
    if room.neighbors.get("E") is None:
        pygame.draw.rect(
            surface, WALL_COLOR,
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
    assert_symmetric(ROOMS)
    assert_connected(ROOMS, START_ROOM)

    clock = pygame.time.Clock()
    running = True
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    current_room = ROOMS[START_ROOM]
    px, py = PLAYER_X, PLAYER_Y

    while running:
        for event in event_getter():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        move_result = move_player(px, py, pygame.key.get_pressed(), room=current_room)

        if isinstance(move_result[0], str):
            direction = move_result[1]
            current_room, px, py = _warp_position(current_room, direction, px, py)
        else:
            px, py = move_result

        draw_room(logical_surface, current_room)
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
