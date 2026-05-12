# bdb1c1b58ad0547a
# Batch: BAT-D83461
# Feature witness: bdb1c1b58ad0547a
# Tests for:
#   REQ-07C0B4 — Room background renders as a single solid color rectangle filling the inner area
#   REQ-82B4D1 — Four wall rectangles render around the full perimeter with no passage gaps
#   REQ-16D6CB — Player square renders at deterministic coordinates near room center
#   REQ-05A20B — Player square dimensions match configured size constant

import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
import importlib
from unittest.mock import patch, call
import pytest

import pygame

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_adventure():
    """Import (or reload) the adventure module so each test gets a fresh state."""
    if "adventure" in sys.modules:
        return sys.modules["adventure"]
    import adventure  # noqa: PLC0415
    return adventure


def _make_surface(w: int, h: int) -> pygame.Surface:
    """Return an off-screen pygame Surface of the given dimensions."""
    pygame.display.init()
    return pygame.Surface((w, h))


# ---------------------------------------------------------------------------
# REQ-07C0B4 — draw_background() fills the inner area with a single solid color
# ---------------------------------------------------------------------------

class TestBackgroundFillsInnerArea:
    """REQ-07C0B4: Room background renders as a single solid color rectangle filling the inner area."""

    def test_background_fills_inner_area(self):
        """draw_background() must call pygame.draw.rect exactly once and the rect must
        cover the full inner (non-wall) area of the logical canvas."""
        adventure = _get_adventure()

        # Ensure the function exists on the module — if it does not, the test fails.
        assert hasattr(adventure, "draw_background"), (
            "adventure.draw_background() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_background(surface)

        # Exactly one fill rect must be drawn (single solid color).
        assert mock_rect.call_count == 1, (
            f"draw_background() must call pygame.draw.rect exactly once, "
            f"got {mock_rect.call_count} call(s)."
        )

        # The rect passed must be non-zero in both dimensions and must lie within the canvas.
        _, kwargs_or_pos = mock_rect.call_args[0], mock_rect.call_args
        args = mock_rect.call_args[0]
        # args: (surface, color, rect, ...)
        assert len(args) >= 3, "pygame.draw.rect must receive at least (surface, color, rect)."
        drawn_rect = pygame.Rect(args[2])

        assert drawn_rect.width > 0, "Background rect must have positive width."
        assert drawn_rect.height > 0, "Background rect must have positive height."
        assert drawn_rect.width <= adventure.LOGICAL_W, (
            "Background rect width must not exceed the logical canvas width."
        )
        assert drawn_rect.height <= adventure.LOGICAL_H, (
            "Background rect height must not exceed the logical canvas height."
        )

    def test_background_uses_single_color(self):
        """draw_background() must draw with a single, consistent color value."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_background"), (
            "adventure.draw_background() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_background(surface)

        args = mock_rect.call_args[0]
        color = args[1]
        # Color must be a 3- or 4-tuple (RGB or RGBA) or a pygame.Color instance.
        assert len(color) in (3, 4), (
            f"draw_background() color must be RGB or RGBA, got: {color!r}"
        )


# ---------------------------------------------------------------------------
# REQ-82B4D1 — draw_walls() draws exactly 4 rects covering all perimeter sides
# ---------------------------------------------------------------------------

class TestFourWallsNoGaps:
    """REQ-82B4D1: Four wall rectangles render around the full perimeter with no passage gaps."""

    def test_four_walls_no_gaps(self):
        """draw_walls() must call pygame.draw.rect exactly 4 times, one per perimeter side."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_walls"), (
            "adventure.draw_walls() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_walls(surface)

        assert mock_rect.call_count == 4, (
            f"draw_walls() must call pygame.draw.rect exactly 4 times (one per side), "
            f"got {mock_rect.call_count} call(s)."
        )

    def test_walls_cover_top_perimeter(self):
        """At least one wall rect must touch the top edge (y == 0)."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_walls"), (
            "adventure.draw_walls() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_walls(surface)

        rects = [pygame.Rect(c[0][2]) for c in mock_rect.call_args_list]
        top_walls = [r for r in rects if r.top == 0]
        assert len(top_walls) >= 1, (
            "At least one wall rect must be positioned at the top edge (y == 0)."
        )

    def test_walls_cover_bottom_perimeter(self):
        """At least one wall rect must touch the bottom edge."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_walls"), (
            "adventure.draw_walls() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_walls(surface)

        rects = [pygame.Rect(c[0][2]) for c in mock_rect.call_args_list]
        bottom_walls = [r for r in rects if r.bottom == adventure.LOGICAL_H]
        assert len(bottom_walls) >= 1, (
            "At least one wall rect must reach the bottom edge of the canvas."
        )

    def test_walls_cover_left_perimeter(self):
        """At least one wall rect must touch the left edge (x == 0)."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_walls"), (
            "adventure.draw_walls() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_walls(surface)

        rects = [pygame.Rect(c[0][2]) for c in mock_rect.call_args_list]
        left_walls = [r for r in rects if r.left == 0]
        assert len(left_walls) >= 1, (
            "At least one wall rect must be positioned at the left edge (x == 0)."
        )

    def test_walls_cover_right_perimeter(self):
        """At least one wall rect must touch the right edge."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_walls"), (
            "adventure.draw_walls() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_walls(surface)

        rects = [pygame.Rect(c[0][2]) for c in mock_rect.call_args_list]
        right_walls = [r for r in rects if r.right == adventure.LOGICAL_W]
        assert len(right_walls) >= 1, (
            "At least one wall rect must reach the right edge of the canvas."
        )


# ---------------------------------------------------------------------------
# REQ-16D6CB — draw_player() draws at deterministic coordinates near room center
# ---------------------------------------------------------------------------

class TestPlayerAtDeterministicCoords:
    """REQ-16D6CB: Player square renders at deterministic coordinates near room center."""

    def test_player_at_deterministic_coords(self):
        """draw_player() must draw the player at constants PLAYER_START_X / PLAYER_START_Y,
        which must be defined on the adventure module and lie within the inner room area."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_player"), (
            "adventure.draw_player() does not exist; implementation required."
        )
        assert hasattr(adventure, "PLAYER_START_X"), (
            "adventure.PLAYER_START_X constant does not exist; implementation required."
        )
        assert hasattr(adventure, "PLAYER_START_Y"), (
            "adventure.PLAYER_START_Y constant does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_player(surface)

        assert mock_rect.call_count >= 1, (
            "draw_player() must call pygame.draw.rect at least once."
        )

        args = mock_rect.call_args[0]
        drawn_rect = pygame.Rect(args[2])

        assert drawn_rect.x == adventure.PLAYER_START_X, (
            f"Player x must equal PLAYER_START_X ({adventure.PLAYER_START_X}), "
            f"got {drawn_rect.x}."
        )
        assert drawn_rect.y == adventure.PLAYER_START_Y, (
            f"Player y must equal PLAYER_START_Y ({adventure.PLAYER_START_Y}), "
            f"got {drawn_rect.y}."
        )

    def test_player_start_coords_near_center(self):
        """PLAYER_START_X and PLAYER_START_Y must be in the middle 50% of the canvas
        (i.e., within the central half of LOGICAL_W and LOGICAL_H respectively)."""
        adventure = _get_adventure()

        assert hasattr(adventure, "PLAYER_START_X"), (
            "adventure.PLAYER_START_X constant does not exist; implementation required."
        )
        assert hasattr(adventure, "PLAYER_START_Y"), (
            "adventure.PLAYER_START_Y constant does not exist; implementation required."
        )

        quarter_w = adventure.LOGICAL_W // 4
        quarter_h = adventure.LOGICAL_H // 4

        assert quarter_w <= adventure.PLAYER_START_X <= adventure.LOGICAL_W - quarter_w, (
            f"PLAYER_START_X ({adventure.PLAYER_START_X}) must be in the central 50% "
            f"of LOGICAL_W ({adventure.LOGICAL_W}); expected range [{quarter_w}, "
            f"{adventure.LOGICAL_W - quarter_w}]."
        )
        assert quarter_h <= adventure.PLAYER_START_Y <= adventure.LOGICAL_H - quarter_h, (
            f"PLAYER_START_Y ({adventure.PLAYER_START_Y}) must be in the central 50% "
            f"of LOGICAL_H ({adventure.LOGICAL_H}); expected range [{quarter_h}, "
            f"{adventure.LOGICAL_H - quarter_h}]."
        )

    def test_player_coords_are_reproducible_across_calls(self):
        """draw_player() must draw at the same coordinates on every call (deterministic)."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_player"), (
            "adventure.draw_player() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        positions = []
        for _ in range(3):
            with patch("pygame.draw.rect") as mock_rect:
                adventure.draw_player(surface)
            args = mock_rect.call_args[0]
            r = pygame.Rect(args[2])
            positions.append((r.x, r.y))

        assert len(set(positions)) == 1, (
            f"draw_player() returned different positions across calls: {positions}. "
            "Rendering must be deterministic."
        )


# ---------------------------------------------------------------------------
# REQ-05A20B — Player square dimensions match PLAYER_SIZE constant
# ---------------------------------------------------------------------------

class TestPlayerSizeMatchesConstant:
    """REQ-05A20B: Player square dimensions match configured size constant."""

    def test_player_size_matches_constant(self):
        """draw_player() must draw a rect whose width and height both equal PLAYER_SIZE."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_player"), (
            "adventure.draw_player() does not exist; implementation required."
        )
        assert hasattr(adventure, "PLAYER_SIZE"), (
            "adventure.PLAYER_SIZE constant does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_player(surface)

        args = mock_rect.call_args[0]
        drawn_rect = pygame.Rect(args[2])

        assert drawn_rect.width == adventure.PLAYER_SIZE, (
            f"Player rect width ({drawn_rect.width}) must equal "
            f"PLAYER_SIZE ({adventure.PLAYER_SIZE})."
        )
        assert drawn_rect.height == adventure.PLAYER_SIZE, (
            f"Player rect height ({drawn_rect.height}) must equal "
            f"PLAYER_SIZE ({adventure.PLAYER_SIZE})."
        )

    def test_player_size_constant_is_positive(self):
        """PLAYER_SIZE must be a positive integer."""
        adventure = _get_adventure()

        assert hasattr(adventure, "PLAYER_SIZE"), (
            "adventure.PLAYER_SIZE constant does not exist; implementation required."
        )

        assert isinstance(adventure.PLAYER_SIZE, int), (
            f"PLAYER_SIZE must be an int, got {type(adventure.PLAYER_SIZE).__name__}."
        )
        assert adventure.PLAYER_SIZE > 0, (
            f"PLAYER_SIZE must be positive, got {adventure.PLAYER_SIZE}."
        )

    def test_player_is_a_square(self):
        """The player rect must be square — width must equal height."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_player"), (
            "adventure.draw_player() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_player(surface)

        args = mock_rect.call_args[0]
        drawn_rect = pygame.Rect(args[2])

        assert drawn_rect.width == drawn_rect.height, (
            f"Player must be a square (width == height), "
            f"got width={drawn_rect.width}, height={drawn_rect.height}."
        )

    def test_player_fits_within_inner_area(self):
        """The player rect must fit entirely within the logical canvas boundaries."""
        adventure = _get_adventure()

        assert hasattr(adventure, "draw_player"), (
            "adventure.draw_player() does not exist; implementation required."
        )

        surface = _make_surface(adventure.LOGICAL_W, adventure.LOGICAL_H)

        with patch("pygame.draw.rect") as mock_rect:
            adventure.draw_player(surface)

        args = mock_rect.call_args[0]
        drawn_rect = pygame.Rect(args[2])

        canvas = pygame.Rect(0, 0, adventure.LOGICAL_W, adventure.LOGICAL_H)
        assert canvas.contains(drawn_rect), (
            f"Player rect {drawn_rect} does not fit within the canvas {canvas}."
        )
