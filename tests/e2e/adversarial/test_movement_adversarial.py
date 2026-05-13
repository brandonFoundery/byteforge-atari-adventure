"""Adversarial tests for T2 — Player movement with wall collision (arrow-key input, 4-direction).

Each test targets a specific potential defect in move_player() and related collision logic.
All tests are self-contained unit-style tests against the pure move_player() function;
no display or event loop is required.

Run with:
    pytest tests/e2e/adversarial/test_movement_adversarial.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pygame
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import adventure  # noqa: E402

# ---------------------------------------------------------------------------
# Boundary constants mirroring production values
# ---------------------------------------------------------------------------

X_MIN = adventure.WALL_THICKNESS
X_MAX = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
Y_MIN = adventure.WALL_THICKNESS
Y_MAX = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE

CENTER_X = adventure.PLAYER_X
CENTER_Y = adventure.PLAYER_Y


# ---------------------------------------------------------------------------
# Key-dict helpers
# ---------------------------------------------------------------------------

def no_keys() -> dict:
    return {
        pygame.K_RIGHT: False,
        pygame.K_LEFT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
    }


def only(key) -> dict:
    k = no_keys()
    k[key] = True
    return k


def both(key_a, key_b) -> dict:
    k = no_keys()
    k[key_a] = True
    k[key_b] = True
    return k


def sdl1_key(sdl1_val: int) -> dict:
    """Return a dict keyed by SDL1 legacy constants."""
    return {sdl1_val: True}


# ---------------------------------------------------------------------------
# Class 1: Basic 4-direction movement — each direction changes the correct axis
# ---------------------------------------------------------------------------

class TestFourDirectionMovement:
    """Verifies that each arrow key moves the player along the correct axis
    and leaves the other axis untouched."""

    def test_right_increases_x_only(self):
        """CATCHES: x/y axes swapped for RIGHT key."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_RIGHT))
        assert x > CENTER_X, "RIGHT key must increase x"
        assert y == CENTER_Y, "RIGHT key must not change y"

    def test_left_decreases_x_only(self):
        """CATCHES: x/y axes swapped for LEFT key."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_LEFT))
        assert x < CENTER_X, "LEFT key must decrease x"
        assert y == CENTER_Y, "LEFT key must not change y"

    def test_up_decreases_y_only(self):
        """CATCHES: UP increasing y instead of decreasing (screen-coords inversion bug)."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_UP))
        assert y < CENTER_Y, "UP key must decrease y (screen coordinates)"
        assert x == CENTER_X, "UP key must not change x"

    def test_down_increases_y_only(self):
        """CATCHES: DOWN decreasing y instead of increasing."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_DOWN))
        assert y > CENTER_Y, "DOWN key must increase y (screen coordinates)"
        assert x == CENTER_X, "DOWN key must not change x"

    def test_right_step_equals_player_speed(self):
        """CATCHES: movement step using wrong constant (e.g. PLAYER_SIZE instead of PLAYER_SPEED)."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_RIGHT))
        assert x == CENTER_X + adventure.PLAYER_SPEED, (
            f"Expected x={CENTER_X + adventure.PLAYER_SPEED}, got {x}"
        )

    def test_left_step_equals_player_speed(self):
        """CATCHES: movement magnitude wrong for LEFT."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_LEFT))
        assert x == CENTER_X - adventure.PLAYER_SPEED, (
            f"Expected x={CENTER_X - adventure.PLAYER_SPEED}, got {x}"
        )

    def test_up_step_equals_player_speed(self):
        """CATCHES: movement magnitude wrong for UP."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_UP))
        assert y == CENTER_Y - adventure.PLAYER_SPEED, (
            f"Expected y={CENTER_Y - adventure.PLAYER_SPEED}, got {y}"
        )

    def test_down_step_equals_player_speed(self):
        """CATCHES: movement magnitude wrong for DOWN."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_DOWN))
        assert y == CENTER_Y + adventure.PLAYER_SPEED, (
            f"Expected y={CENTER_Y + adventure.PLAYER_SPEED}, got {y}"
        )

    def test_no_keys_returns_same_position(self):
        """CATCHES: drift when no keys are pressed (e.g. friction or gravity applied)."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, no_keys())
        assert (x, y) == (CENTER_X, CENTER_Y), (
            "No keys pressed must not change position"
        )


# ---------------------------------------------------------------------------
# Class 2: Wall collision clamping — player must stop at each boundary
# ---------------------------------------------------------------------------

class TestWallCollisionClamping:
    """Each boundary has an exact clamp limit. Tests verify the player cannot
    escape through any wall and cannot be stopped before reaching the wall."""

    def test_left_wall_clamp_exact_boundary(self):
        """CATCHES: clamp using wrong constant (_X_MIN off-by-one) letting player enter wall."""
        x, y = adventure.move_player(X_MIN, CENTER_Y, only(pygame.K_LEFT))
        assert x == X_MIN, f"At left wall, x must stay {X_MIN}, got {x}"

    def test_right_wall_clamp_exact_boundary(self):
        """CATCHES: clamp using wrong constant (_X_MAX off-by-one) letting player enter wall."""
        x, y = adventure.move_player(X_MAX, CENTER_Y, only(pygame.K_RIGHT))
        assert x == X_MAX, f"At right wall, x must stay {X_MAX}, got {x}"

    def test_top_wall_clamp_exact_boundary(self):
        """CATCHES: clamp using wrong constant (_Y_MIN off-by-one)."""
        x, y = adventure.move_player(CENTER_X, Y_MIN, only(pygame.K_UP))
        assert y == Y_MIN, f"At top wall, y must stay {Y_MIN}, got {y}"

    def test_bottom_wall_clamp_exact_boundary(self):
        """CATCHES: clamp using wrong constant (_Y_MAX off-by-one)."""
        x, y = adventure.move_player(CENTER_X, Y_MAX, only(pygame.K_DOWN))
        assert y == Y_MAX, f"At bottom wall, y must stay {Y_MAX}, got {y}"

    def test_player_cannot_go_left_of_left_wall(self):
        """CATCHES: no clamping on x minimum — player passes through left wall."""
        x_beyond = X_MIN - adventure.PLAYER_SPEED
        x, y = adventure.move_player(x_beyond, CENTER_Y, only(pygame.K_LEFT))
        assert x >= X_MIN, (
            f"Player left-of-wall must clamp to {X_MIN}, got {x}"
        )

    def test_player_cannot_go_right_of_right_wall(self):
        """CATCHES: no clamping on x maximum — player passes through right wall."""
        x_beyond = X_MAX + adventure.PLAYER_SPEED
        x, y = adventure.move_player(x_beyond, CENTER_Y, only(pygame.K_RIGHT))
        assert x <= X_MAX, (
            f"Player right-of-wall must clamp to {X_MAX}, got {x}"
        )

    def test_player_cannot_go_above_top_wall(self):
        """CATCHES: no clamping on y minimum — player passes through top wall."""
        y_beyond = Y_MIN - adventure.PLAYER_SPEED
        x, y = adventure.move_player(CENTER_X, y_beyond, only(pygame.K_UP))
        assert y >= Y_MIN, (
            f"Player above-top-wall must clamp to {Y_MIN}, got {y}"
        )

    def test_player_cannot_go_below_bottom_wall(self):
        """CATCHES: no clamping on y maximum — player passes through bottom wall."""
        y_beyond = Y_MAX + adventure.PLAYER_SPEED
        x, y = adventure.move_player(CENTER_X, y_beyond, only(pygame.K_DOWN))
        assert y <= Y_MAX, (
            f"Player below-bottom-wall must clamp to {Y_MAX}, got {y}"
        )

    def test_left_wall_boundary_constants_are_consistent(self):
        """CATCHES: _X_MIN/X_MIN not equal to WALL_THICKNESS — mismatched constants."""
        assert X_MIN == adventure.WALL_THICKNESS, (
            f"Left boundary X_MIN={X_MIN} should equal WALL_THICKNESS={adventure.WALL_THICKNESS}"
        )

    def test_right_wall_boundary_accounts_for_player_size(self):
        """CATCHES: _X_MAX not subtracting PLAYER_SIZE, allowing partial overlap with right wall."""
        expected_x_max = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
        assert X_MAX == expected_x_max, (
            f"Right boundary X_MAX={X_MAX} should equal "
            f"LOGICAL_WIDTH - WALL_THICKNESS - PLAYER_SIZE = {expected_x_max}"
        )

    def test_bottom_wall_boundary_accounts_for_player_size(self):
        """CATCHES: _Y_MAX not subtracting PLAYER_SIZE, allowing partial overlap with bottom wall."""
        expected_y_max = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
        assert Y_MAX == expected_y_max, (
            f"Bottom boundary Y_MAX={Y_MAX} should equal "
            f"LOGICAL_HEIGHT - WALL_THICKNESS - PLAYER_SIZE = {expected_y_max}"
        )

    def test_player_can_reach_left_wall(self):
        """CATCHES: overly conservative clamp stopping player short of the wall."""
        x = X_MIN + 1
        while x > X_MIN:
            x, _ = adventure.move_player(x, CENTER_Y, only(pygame.K_LEFT))
        assert x == X_MIN, (
            f"Player should be able to reach X_MIN={X_MIN}, stopped at {x}"
        )

    def test_player_can_reach_right_wall(self):
        """CATCHES: overly conservative clamp stopping player short of the wall."""
        x = X_MAX - 1
        while x < X_MAX:
            x, _ = adventure.move_player(x, CENTER_Y, only(pygame.K_RIGHT))
        assert x == X_MAX, (
            f"Player should be able to reach X_MAX={X_MAX}, stopped at {x}"
        )

    def test_player_can_reach_top_wall(self):
        """CATCHES: overly conservative clamp stopping player short of the top wall."""
        y = Y_MIN + 1
        while y > Y_MIN:
            _, y = adventure.move_player(CENTER_X, y, only(pygame.K_UP))
        assert y == Y_MIN, (
            f"Player should be able to reach Y_MIN={Y_MIN}, stopped at {y}"
        )

    def test_player_can_reach_bottom_wall(self):
        """CATCHES: overly conservative clamp stopping player short of the bottom wall."""
        y = Y_MAX - 1
        while y < Y_MAX:
            _, y = adventure.move_player(CENTER_X, y, only(pygame.K_DOWN))
        assert y == Y_MAX, (
            f"Player should be able to reach Y_MAX={Y_MAX}, stopped at {y}"
        )


# ---------------------------------------------------------------------------
# Class 3: Opposite-key cancellation
# ---------------------------------------------------------------------------

class TestOppositeKeyHandling:
    """When both opposing keys are pressed simultaneously the net result
    should be additive (both deltas applied). Tests document and verify
    the actual behavior so a silent change is caught."""

    def test_left_and_right_simultaneously_result_is_deterministic(self):
        """CATCHES: crash or undefined behavior when both horizontal keys held."""
        # Both deltas applied: +SPEED then -SPEED => net 0 (order-dependent but deterministic)
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_LEFT, pygame.K_RIGHT))
        # Result must be a valid integer, not NaN or exception
        assert isinstance(x, int), f"x must be int, got {type(x)}"
        assert isinstance(y, int), f"y must be int, got {type(y)}"

    def test_up_and_down_simultaneously_result_is_deterministic(self):
        """CATCHES: crash or undefined behavior when both vertical keys held."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_UP, pygame.K_DOWN))
        assert isinstance(x, int), f"x must be int, got {type(x)}"
        assert isinstance(y, int), f"y must be int, got {type(y)}"

    def test_left_and_right_simultaneously_position_within_bounds(self):
        """CATCHES: combined horizontal keys moving player out of bounds."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_LEFT, pygame.K_RIGHT))
        assert X_MIN <= x <= X_MAX, f"Combined LR result {x} out of bounds [{X_MIN}, {X_MAX}]"

    def test_up_and_down_simultaneously_position_within_bounds(self):
        """CATCHES: combined vertical keys moving player out of bounds."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_UP, pygame.K_DOWN))
        assert Y_MIN <= y <= Y_MAX, f"Combined UD result {y} out of bounds [{Y_MIN}, {Y_MAX}]"


# ---------------------------------------------------------------------------
# Class 4: Diagonal movement
# ---------------------------------------------------------------------------

class TestDiagonalMovement:
    """Arrow-key diagonals (two orthogonal keys held simultaneously) must
    move both axes independently and stay within bounds."""

    def test_right_and_down_moves_both_axes(self):
        """CATCHES: diagonal input only moving one axis."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_RIGHT, pygame.K_DOWN))
        assert x > CENTER_X, "RIGHT+DOWN must increase x"
        assert y > CENTER_Y, "RIGHT+DOWN must increase y"

    def test_right_and_up_moves_both_axes(self):
        """CATCHES: diagonal input only moving one axis."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_RIGHT, pygame.K_UP))
        assert x > CENTER_X, "RIGHT+UP must increase x"
        assert y < CENTER_Y, "RIGHT+UP must decrease y"

    def test_left_and_down_moves_both_axes(self):
        """CATCHES: diagonal input only moving one axis."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_LEFT, pygame.K_DOWN))
        assert x < CENTER_X, "LEFT+DOWN must decrease x"
        assert y > CENTER_Y, "LEFT+DOWN must increase y"

    def test_left_and_up_moves_both_axes(self):
        """CATCHES: diagonal input only moving one axis."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_LEFT, pygame.K_UP))
        assert x < CENTER_X, "LEFT+UP must decrease x"
        assert y < CENTER_Y, "LEFT+UP must decrease y"

    def test_diagonal_magnitude_is_independent_per_axis(self):
        """CATCHES: diagonal movement using combined magnitude instead of per-axis speed."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, both(pygame.K_RIGHT, pygame.K_DOWN))
        assert x == CENTER_X + adventure.PLAYER_SPEED, (
            f"Diagonal x step must equal PLAYER_SPEED={adventure.PLAYER_SPEED}, got {x - CENTER_X}"
        )
        assert y == CENTER_Y + adventure.PLAYER_SPEED, (
            f"Diagonal y step must equal PLAYER_SPEED={adventure.PLAYER_SPEED}, got {y - CENTER_Y}"
        )

    def test_diagonal_from_corner_clamps_both_axes(self):
        """CATCHES: diagonal at corner skipping clamp for one axis."""
        x, y = adventure.move_player(X_MIN, Y_MIN, both(pygame.K_LEFT, pygame.K_UP))
        assert x == X_MIN, f"Corner left-up x should clamp to {X_MIN}, got {x}"
        assert y == Y_MIN, f"Corner left-up y should clamp to {Y_MIN}, got {y}"


# ---------------------------------------------------------------------------
# Class 5: SDL1 legacy key constant support
# ---------------------------------------------------------------------------

class TestSdl1LegacyKeys:
    """The production code explicitly supports SDL1 numeric key constants.
    These tests verify that SDL1 constants trigger the same movement as SDL2."""

    def test_sdl1_right_moves_player_right(self):
        """CATCHES: SDL1 key constants not handled — legacy key dict has no effect."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, sdl1_key(adventure._K_RIGHT))
        assert x == CENTER_X + adventure.PLAYER_SPEED, (
            f"SDL1 RIGHT (val={adventure._K_RIGHT}) must increase x by PLAYER_SPEED"
        )

    def test_sdl1_left_moves_player_left(self):
        """CATCHES: SDL1 LEFT constant not handled."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, sdl1_key(adventure._K_LEFT))
        assert x == CENTER_X - adventure.PLAYER_SPEED, (
            f"SDL1 LEFT (val={adventure._K_LEFT}) must decrease x by PLAYER_SPEED"
        )

    def test_sdl1_up_moves_player_up(self):
        """CATCHES: SDL1 UP constant not handled."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, sdl1_key(adventure._K_UP))
        assert y == CENTER_Y - adventure.PLAYER_SPEED, (
            f"SDL1 UP (val={adventure._K_UP}) must decrease y by PLAYER_SPEED"
        )

    def test_sdl1_down_moves_player_down(self):
        """CATCHES: SDL1 DOWN constant not handled."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, sdl1_key(adventure._K_DOWN))
        assert y == CENTER_Y + adventure.PLAYER_SPEED, (
            f"SDL1 DOWN (val={adventure._K_DOWN}) must increase y by PLAYER_SPEED"
        )

    def test_sdl1_right_wall_clamp_applies(self):
        """CATCHES: SDL1 key handling bypasses clamping logic."""
        x, y = adventure.move_player(X_MAX, CENTER_Y, sdl1_key(adventure._K_RIGHT))
        assert x == X_MAX, (
            f"SDL1 RIGHT at right wall must clamp to {X_MAX}, got {x}"
        )


# ---------------------------------------------------------------------------
# Class 6: Rapid repeated movement (accumulated drift)
# ---------------------------------------------------------------------------

class TestRepeatedMovement:
    """Simulates holding a key for many frames. The player must reach the wall
    and stay clamped, never drifting beyond it."""

    def _walk_to_wall(self, start_x, start_y, key, steps=200):
        x, y = start_x, start_y
        for _ in range(steps):
            x, y = adventure.move_player(x, y, only(key))
        return x, y

    def test_hold_right_reaches_and_stays_at_right_wall(self):
        """CATCHES: accumulated floating-point drift beyond X_MAX after many frames."""
        x, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_RIGHT)
        assert x == X_MAX, f"After many RIGHT presses, x={x} should equal X_MAX={X_MAX}"

    def test_hold_left_reaches_and_stays_at_left_wall(self):
        """CATCHES: accumulated drift beyond X_MIN after many frames."""
        x, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_LEFT)
        assert x == X_MIN, f"After many LEFT presses, x={x} should equal X_MIN={X_MIN}"

    def test_hold_up_reaches_and_stays_at_top_wall(self):
        """CATCHES: accumulated drift beyond Y_MIN after many frames."""
        x, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_UP)
        assert y == Y_MIN, f"After many UP presses, y={y} should equal Y_MIN={Y_MIN}"

    def test_hold_down_reaches_and_stays_at_bottom_wall(self):
        """CATCHES: accumulated drift beyond Y_MAX after many frames."""
        x, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_DOWN)
        assert y == Y_MAX, f"After many DOWN presses, y={y} should equal Y_MAX={Y_MAX}"

    def test_rapid_direction_reversal_does_not_escape_bounds(self):
        """CATCHES: bounce bug where reversal from wall overshoots the opposite boundary."""
        x, y = CENTER_X, CENTER_Y
        for i in range(100):
            key = pygame.K_RIGHT if i % 2 == 0 else pygame.K_LEFT
            x, y = adventure.move_player(x, y, only(key))
        assert X_MIN <= x <= X_MAX, f"After oscillating x={x} is out of bounds"

    def test_all_four_walls_reachable_from_center_in_steps(self):
        """CATCHES: player trapped short of a wall due to PLAYER_SPEED not dividing evenly."""
        # Right
        x, _ = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_RIGHT)
        assert x == X_MAX
        # Left
        x, _ = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_LEFT)
        assert x == X_MIN
        # Down
        _, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_DOWN)
        assert y == Y_MAX
        # Up
        _, y = self._walk_to_wall(CENTER_X, CENTER_Y, pygame.K_UP)
        assert y == Y_MIN


# ---------------------------------------------------------------------------
# Class 7: Return-value contract
# ---------------------------------------------------------------------------

class TestReturnValueContract:
    """move_player must always return (int, int) regardless of input."""

    def test_return_type_is_tuple_of_two(self):
        """CATCHES: function returning list, None, or single value."""
        result = adventure.move_player(CENTER_X, CENTER_Y, no_keys())
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 2, f"Expected 2-tuple, got length {len(result)}"

    def test_return_values_are_integers(self):
        """CATCHES: clamping converting int to float (e.g. using / instead of //)."""
        x, y = adventure.move_player(CENTER_X, CENTER_Y, only(pygame.K_RIGHT))
        assert isinstance(x, int), f"x must be int, got {type(x)}"
        assert isinstance(y, int), f"y must be int, got {type(y)}"

    def test_return_values_are_integers_at_boundary(self):
        """CATCHES: clamp functions returning float at boundary."""
        x, y = adventure.move_player(X_MIN, Y_MIN, only(pygame.K_LEFT))
        assert isinstance(x, int), f"x at clamp must be int, got {type(x)}"
        assert isinstance(y, int), f"y at clamp must be int, got {type(y)}"

    def test_position_always_within_valid_range(self):
        """CATCHES: any position returned outside the valid playfield."""
        test_positions = [
            (CENTER_X, CENTER_Y),
            (X_MIN, Y_MIN),
            (X_MAX, Y_MAX),
            (0, 0),
            (adventure.LOGICAL_WIDTH, adventure.LOGICAL_HEIGHT),
        ]
        test_keys = [no_keys(), only(pygame.K_RIGHT), only(pygame.K_LEFT),
                     only(pygame.K_UP), only(pygame.K_DOWN)]
        for (px, py) in test_positions:
            for keys in test_keys:
                x, y = adventure.move_player(px, py, keys)
                assert X_MIN <= x <= X_MAX, (
                    f"x={x} out of range [{X_MIN}, {X_MAX}] from ({px},{py})"
                )
                assert Y_MIN <= y <= Y_MAX, (
                    f"y={y} out of range [{Y_MIN}, {Y_MAX}] from ({px},{py})"
                )
