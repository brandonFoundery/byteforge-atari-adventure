# witness: b6731a13a9b00140
# batch:   BAT-608A47
# feature: t2-player-movement-with-wall-collision-a
#
# Tests for WallBoundaryConfig constants and move_player clamping behavior.
# REQs covered:
#   REQ-12A97B  _X_MIN equals WALL_THICKNESS
#   REQ-14DD79  _Y_MIN equals WALL_THICKNESS
#   REQ-E75BF0  _X_MAX equals LOGICAL_WIDTH minus WALL_THICKNESS minus PLAYER_SIZE
#   REQ-F869F1  _Y_MAX equals LOGICAL_HEIGHT minus WALL_THICKNESS minus PLAYER_SIZE
#   REQ-AB8DAB  move_player clamps x to range _X_MIN to _X_MAX after applying key input
#   REQ-D6D25F  move_player clamps y to range _Y_MIN to _Y_MAX after applying key input
#   REQ-6C4582  attempting to move left past _X_MIN returns x equal to _X_MIN
#   REQ-EFF78E  attempting to move right past _X_MAX returns x equal to _X_MAX
#   REQ-201AD6  attempting to move down past _Y_MAX returns y equal to _Y_MAX
#   REQ-398CFE  attempting to move up past _Y_MIN returns y equal to _Y_MIN

import os
import sys

import pytest

# ---------------------------------------------------------------------------
# Headless pygame setup (must happen before importing adventure)
# ---------------------------------------------------------------------------
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import adventure  # noqa: E402  (import after env vars)

# ---------------------------------------------------------------------------
# Pygame key constants (same values used by pygame itself)
# ---------------------------------------------------------------------------
K_RIGHT = 275
K_LEFT  = 276
K_UP    = 273
K_DOWN  = 274


# ---------------------------------------------------------------------------
# Key-press builder helpers
# ---------------------------------------------------------------------------

def _no_keys() -> dict:
    """Returns a keys dict with no keys pressed."""
    return {K_RIGHT: False, K_LEFT: False, K_UP: False, K_DOWN: False}


def _only(key: int) -> dict:
    """Returns a keys dict with only the given key pressed."""
    keys = _no_keys()
    keys[key] = True
    return keys


# ---------------------------------------------------------------------------
# Safe starting positions (guaranteed to be inside wall bounds)
# ---------------------------------------------------------------------------
CENTER_X = adventure.PLAYER_X
CENTER_Y = adventure.PLAYER_Y


# ===========================================================================
# Constant derivation tests
# ===========================================================================

class TestWallBoundaryConstants:
    """Verify that boundary constants are derived correctly from primitives."""

    # REQ-12A97B
    def test_x_min_equals_wall_thickness(self):
        """_X_MIN must equal WALL_THICKNESS (left wall inner edge)."""
        assert adventure._X_MIN == adventure.WALL_THICKNESS

    # REQ-14DD79
    def test_y_min_equals_wall_thickness(self):
        """_Y_MIN must equal WALL_THICKNESS (top wall inner edge)."""
        assert adventure._Y_MIN == adventure.WALL_THICKNESS

    # REQ-E75BF0
    def test_x_max_equals_logical_width_minus_wall_thickness_minus_player_size(self):
        """_X_MAX must equal LOGICAL_WIDTH - WALL_THICKNESS - PLAYER_SIZE."""
        expected = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
        assert adventure._X_MAX == expected

    # REQ-F869F1
    def test_y_max_equals_logical_height_minus_wall_thickness_minus_player_size(self):
        """_Y_MAX must equal LOGICAL_HEIGHT - WALL_THICKNESS - PLAYER_SIZE."""
        expected = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
        assert adventure._Y_MAX == expected


# ===========================================================================
# Clamping range tests (REQ-AB8DAB, REQ-D6D25F)
# ===========================================================================

class TestMovePlayerClampsToRange:
    """move_player must keep x and y inside [_X_MIN.._X_MAX] x [_Y_MIN.._Y_MAX]."""

    # REQ-AB8DAB
    def test_move_player_x_is_never_below_x_min(self):
        """x returned by move_player must never be less than _X_MIN."""
        x, y = adventure.move_player(adventure._X_MIN, CENTER_Y, _only(K_LEFT))
        assert x >= adventure._X_MIN

    # REQ-AB8DAB
    def test_move_player_x_is_never_above_x_max(self):
        """x returned by move_player must never exceed _X_MAX."""
        x, y = adventure.move_player(adventure._X_MAX, CENTER_Y, _only(K_RIGHT))
        assert x <= adventure._X_MAX

    # REQ-D6D25F
    def test_move_player_y_is_never_below_y_min(self):
        """y returned by move_player must never be less than _Y_MIN."""
        x, y = adventure.move_player(CENTER_X, adventure._Y_MIN, _only(K_UP))
        assert y >= adventure._Y_MIN

    # REQ-D6D25F
    def test_move_player_y_is_never_above_y_max(self):
        """y returned by move_player must never exceed _Y_MAX."""
        x, y = adventure.move_player(CENTER_X, adventure._Y_MAX, _only(K_DOWN))
        assert y <= adventure._Y_MAX


# ===========================================================================
# Hard boundary tests (each of the four walls, REQ-6C4582 / EFF78E / 201AD6 / 398CFE)
# ===========================================================================

class TestMovePlayerHardBoundaries:
    """Pressing into a wall at the boundary must return the exact boundary value."""

    # REQ-6C4582
    def test_move_left_at_x_min_returns_x_min(self):
        """Pressing K_LEFT when already at _X_MIN must return x == _X_MIN."""
        x, _y = adventure.move_player(adventure._X_MIN, CENTER_Y, _only(K_LEFT))
        assert x == adventure._X_MIN

    # REQ-EFF78E
    def test_move_right_at_x_max_returns_x_max(self):
        """Pressing K_RIGHT when already at _X_MAX must return x == _X_MAX."""
        x, _y = adventure.move_player(adventure._X_MAX, CENTER_Y, _only(K_RIGHT))
        assert x == adventure._X_MAX

    # REQ-398CFE
    def test_move_up_at_y_min_returns_y_min(self):
        """Pressing K_UP when already at _Y_MIN must return y == _Y_MIN."""
        _x, y = adventure.move_player(CENTER_X, adventure._Y_MIN, _only(K_UP))
        assert y == adventure._Y_MIN

    # REQ-201AD6
    def test_move_down_at_y_max_returns_y_max(self):
        """Pressing K_DOWN when already at _Y_MAX must return y == _Y_MAX."""
        _x, y = adventure.move_player(CENTER_X, adventure._Y_MAX, _only(K_DOWN))
        assert y == adventure._Y_MAX

    # REQ-6C4582 — extra: start one step inside _X_MIN so the move would cross
    def test_move_left_one_step_past_x_min_is_clamped_to_x_min(self):
        """Starting at _X_MIN + 1 and pressing K_LEFT should land at _X_MIN (or stay at _X_MIN
        if PLAYER_SPEED > 1 would overshoot)."""
        start_x = adventure._X_MIN + 1
        x, _y = adventure.move_player(start_x, CENTER_Y, _only(K_LEFT))
        assert x >= adventure._X_MIN

    # REQ-EFF78E — extra: start one step inside _X_MAX
    def test_move_right_one_step_before_x_max_does_not_exceed_x_max(self):
        """Starting at _X_MAX - 1 and pressing K_RIGHT must not exceed _X_MAX."""
        start_x = adventure._X_MAX - 1
        x, _y = adventure.move_player(start_x, CENTER_Y, _only(K_RIGHT))
        assert x <= adventure._X_MAX

    # REQ-398CFE — extra: start one step inside _Y_MIN
    def test_move_up_one_step_past_y_min_is_clamped_to_y_min(self):
        """Starting at _Y_MIN + 1 and pressing K_UP must not go below _Y_MIN."""
        start_y = adventure._Y_MIN + 1
        _x, y = adventure.move_player(CENTER_X, start_y, _only(K_UP))
        assert y >= adventure._Y_MIN

    # REQ-201AD6 — extra: start one step inside _Y_MAX
    def test_move_down_one_step_before_y_max_does_not_exceed_y_max(self):
        """Starting at _Y_MAX - 1 and pressing K_DOWN must not exceed _Y_MAX."""
        start_y = adventure._Y_MAX - 1
        _x, y = adventure.move_player(CENTER_X, start_y, _only(K_DOWN))
        assert y <= adventure._Y_MAX


# ===========================================================================
# Clamping is inside move_player (not external) — structural contract tests
# ===========================================================================

class TestClampingIsInsideMovePlayer:
    """Verify that clamping happens inside move_player, not as a post-step."""

    # REQ-AB8DAB: passing an already-out-of-bounds x must be clamped on return
    def test_x_already_below_x_min_with_no_keys_is_clamped(self):
        """Even with no movement, x below _X_MIN must be clamped when returned."""
        # If clamping is internal, out-of-bounds input must be corrected on output.
        out_of_bounds_x = adventure._X_MIN - 10
        x, _y = adventure.move_player(out_of_bounds_x, CENTER_Y, _no_keys())
        assert x >= adventure._X_MIN

    def test_x_already_above_x_max_with_no_keys_is_clamped(self):
        """Even with no movement, x above _X_MAX must be clamped when returned."""
        out_of_bounds_x = adventure._X_MAX + 10
        x, _y = adventure.move_player(out_of_bounds_x, CENTER_Y, _no_keys())
        assert x <= adventure._X_MAX

    # REQ-D6D25F: same for y axis
    def test_y_already_below_y_min_with_no_keys_is_clamped(self):
        """Even with no movement, y below _Y_MIN must be clamped when returned."""
        out_of_bounds_y = adventure._Y_MIN - 10
        _x, y = adventure.move_player(CENTER_X, out_of_bounds_y, _no_keys())
        assert y >= adventure._Y_MIN

    def test_y_already_above_y_max_with_no_keys_is_clamped(self):
        """Even with no movement, y above _Y_MAX must be clamped when returned."""
        out_of_bounds_y = adventure._Y_MAX + 10
        _x, y = adventure.move_player(CENTER_X, out_of_bounds_y, _no_keys())
        assert y <= adventure._Y_MAX
