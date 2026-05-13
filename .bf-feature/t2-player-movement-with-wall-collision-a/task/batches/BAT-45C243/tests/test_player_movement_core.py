# witness: b6731a13a9b00140
# batch: BAT-45C243
# feature: t2-player-movement-with-wall-collision-a
#
# Tests for PlayerMovementCore batch covering:
#   REQ-077E89, REQ-61A105, REQ-9463A3, REQ-7B8D30,
#   REQ-77D5D3, REQ-D70100, REQ-68475D, REQ-995830,
#   REQ-A617E0, REQ-DEEA15
#
# Run from repo root: pytest .bf-feature/.../tests/test_player_movement_core.py

import os
import sys
import types
import importlib
from unittest.mock import MagicMock, patch, call

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_keys(held: set) -> dict:
    """Build a dict keyed by pygame key constants where True means held.

    pygame key constants used:
        K_RIGHT = 275
        K_LEFT  = 276
        K_UP    = 273
        K_DOWN  = 274
    """
    K_RIGHT = 275
    K_LEFT  = 276
    K_UP    = 273
    K_DOWN  = 274

    all_keys = {K_RIGHT, K_LEFT, K_UP, K_DOWN}
    return {k: (k in held) for k in all_keys}


def _import_adventure():
    """Import the adventure module, providing a minimal pygame stub if needed."""
    # Provide a minimal pygame stub so the module can be imported in headless envs.
    if "pygame" not in sys.modules:
        pygame_stub = types.ModuleType("pygame")

        # key sub-module with constants
        key_mod = types.ModuleType("pygame.key")
        key_mod.get_pressed = MagicMock(return_value={})
        pygame_stub.key = key_mod

        # minimal constants
        pygame_stub.K_RIGHT = 275
        pygame_stub.K_LEFT  = 276
        pygame_stub.K_UP    = 273
        pygame_stub.K_DOWN  = 274

        pygame_stub.init        = MagicMock(return_value=(1, 0))
        pygame_stub.quit        = MagicMock()
        pygame_stub.display     = MagicMock()
        pygame_stub.event       = MagicMock()
        pygame_stub.time        = MagicMock()
        pygame_stub.draw        = MagicMock()
        pygame_stub.Surface     = MagicMock()
        pygame_stub.QUIT        = 12
        pygame_stub.KEYDOWN     = 2
        pygame_stub.K_ESCAPE    = 27
        pygame_stub.transform   = MagicMock()
        pygame_stub.font        = MagicMock()
        pygame_stub.image       = MagicMock()
        pygame_stub.Rect        = MagicMock(side_effect=lambda *a, **kw: MagicMock())

        sys.modules["pygame"]     = pygame_stub
        sys.modules["pygame.key"] = key_mod

    # Ensure repo root is on sys.path so `import adventure` resolves.
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", "..")
    )
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    return importlib.import_module("adventure")


# ---------------------------------------------------------------------------
# REQ-61A105 — PLAYER_SPEED constant
# ---------------------------------------------------------------------------

class TestPlayerSpeedConstant:
    """PLAYER_SPEED constant exists in adventure module with a positive integer value."""

    def test_player_speed_exists(self):
        """REQ-61A105: adventure module exposes PLAYER_SPEED attribute."""
        adventure = _import_adventure()
        assert hasattr(adventure, "PLAYER_SPEED"), (
            "PLAYER_SPEED constant not found in adventure module"
        )

    def test_player_speed_is_integer(self):
        """REQ-61A105: PLAYER_SPEED is an integer."""
        adventure = _import_adventure()
        assert isinstance(adventure.PLAYER_SPEED, int), (
            f"PLAYER_SPEED must be an int, got {type(adventure.PLAYER_SPEED)}"
        )

    def test_player_speed_is_positive(self):
        """REQ-61A105: PLAYER_SPEED is greater than zero."""
        adventure = _import_adventure()
        assert adventure.PLAYER_SPEED > 0, (
            f"PLAYER_SPEED must be positive, got {adventure.PLAYER_SPEED}"
        )


# ---------------------------------------------------------------------------
# REQ-077E89 — move_player signature and return value
# ---------------------------------------------------------------------------

class TestMovePlayerSignature:
    """adventure.move_player accepts x, y, keys_pressed and returns updated x, y."""

    def test_move_player_callable(self):
        """REQ-077E89: adventure module exposes a callable move_player."""
        adventure = _import_adventure()
        assert callable(getattr(adventure, "move_player", None)), (
            "move_player not found or not callable in adventure module"
        )

    def test_move_player_returns_two_values(self):
        """REQ-077E89: move_player returns a 2-tuple (x, y)."""
        adventure = _import_adventure()
        keys = _make_keys(set())
        result = adventure.move_player(100, 100, keys)
        assert len(result) == 2, (
            f"move_player must return exactly 2 values, got {len(result)}"
        )

    def test_move_player_return_values_are_numeric(self):
        """REQ-077E89: both returned values are numeric (int or float)."""
        adventure = _import_adventure()
        keys = _make_keys(set())
        new_x, new_y = adventure.move_player(50, 50, keys)
        assert isinstance(new_x, (int, float)), "returned x must be numeric"
        assert isinstance(new_y, (int, float)), "returned y must be numeric"


# ---------------------------------------------------------------------------
# REQ-68475D — no keys pressed returns x and y unchanged
# ---------------------------------------------------------------------------

class TestNoKeysPressedReturnUnchanged:
    """move_player with no keys pressed returns x and y unchanged."""

    def test_no_keys_x_unchanged(self):
        """REQ-68475D: x is unchanged when no directional keys are pressed."""
        adventure = _import_adventure()
        keys = _make_keys(set())
        new_x, _ = adventure.move_player(42, 99, keys)
        assert new_x == 42, f"Expected x=42 with no keys, got {new_x}"

    def test_no_keys_y_unchanged(self):
        """REQ-68475D: y is unchanged when no directional keys are pressed."""
        adventure = _import_adventure()
        keys = _make_keys(set())
        _, new_y = adventure.move_player(42, 99, keys)
        assert new_y == 99, f"Expected y=99 with no keys, got {new_y}"

    def test_no_keys_origin_unchanged(self):
        """REQ-68475D: position (0, 0) stays (0, 0) with no keys pressed."""
        adventure = _import_adventure()
        keys = _make_keys(set())
        result = adventure.move_player(0, 0, keys)
        assert result == (0, 0), f"Expected (0, 0) with no keys, got {result}"


# ---------------------------------------------------------------------------
# REQ-9463A3 — K_RIGHT increments x by PLAYER_SPEED
# ---------------------------------------------------------------------------

class TestMoveRight:
    """Pressing K_RIGHT returns x incremented by PLAYER_SPEED."""

    def test_right_increments_x_by_player_speed(self):
        """REQ-9463A3: x increases by exactly PLAYER_SPEED when K_RIGHT held."""
        adventure = _import_adventure()
        speed = adventure.PLAYER_SPEED
        keys = _make_keys({275})  # K_RIGHT
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50 + speed, (
            f"Expected x={50 + speed} with K_RIGHT, got {new_x}"
        )

    def test_right_does_not_change_y(self):
        """REQ-9463A3: y is unchanged when only K_RIGHT is held."""
        adventure = _import_adventure()
        keys = _make_keys({275})
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50, f"Expected y=50 with only K_RIGHT, got {new_y}"


# ---------------------------------------------------------------------------
# REQ-7B8D30 — K_LEFT decrements x by PLAYER_SPEED
# ---------------------------------------------------------------------------

class TestMoveLeft:
    """Pressing K_LEFT returns x decremented by PLAYER_SPEED."""

    def test_left_decrements_x_by_player_speed(self):
        """REQ-7B8D30: x decreases by exactly PLAYER_SPEED when K_LEFT held."""
        adventure = _import_adventure()
        speed = adventure.PLAYER_SPEED
        keys = _make_keys({276})  # K_LEFT
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50 - speed, (
            f"Expected x={50 - speed} with K_LEFT, got {new_x}"
        )

    def test_left_does_not_change_y(self):
        """REQ-7B8D30: y is unchanged when only K_LEFT is held."""
        adventure = _import_adventure()
        keys = _make_keys({276})
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50, f"Expected y=50 with only K_LEFT, got {new_y}"


# ---------------------------------------------------------------------------
# REQ-77D5D3 — K_DOWN increments y by PLAYER_SPEED
# ---------------------------------------------------------------------------

class TestMoveDown:
    """Pressing K_DOWN returns y incremented by PLAYER_SPEED."""

    def test_down_increments_y_by_player_speed(self):
        """REQ-77D5D3: y increases by exactly PLAYER_SPEED when K_DOWN held."""
        adventure = _import_adventure()
        speed = adventure.PLAYER_SPEED
        keys = _make_keys({274})  # K_DOWN
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50 + speed, (
            f"Expected y={50 + speed} with K_DOWN, got {new_y}"
        )

    def test_down_does_not_change_x(self):
        """REQ-77D5D3: x is unchanged when only K_DOWN is held."""
        adventure = _import_adventure()
        keys = _make_keys({274})
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50, f"Expected x=50 with only K_DOWN, got {new_x}"


# ---------------------------------------------------------------------------
# REQ-D70100 — K_UP decrements y by PLAYER_SPEED
# ---------------------------------------------------------------------------

class TestMoveUp:
    """Pressing K_UP returns y decremented by PLAYER_SPEED."""

    def test_up_decrements_y_by_player_speed(self):
        """REQ-D70100: y decreases by exactly PLAYER_SPEED when K_UP held."""
        adventure = _import_adventure()
        speed = adventure.PLAYER_SPEED
        keys = _make_keys({273})  # K_UP
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50 - speed, (
            f"Expected y={50 - speed} with K_UP, got {new_y}"
        )

    def test_up_does_not_change_x(self):
        """REQ-D70100: x is unchanged when only K_UP is held."""
        adventure = _import_adventure()
        keys = _make_keys({273})
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50, f"Expected x=50 with only K_UP, got {new_x}"


# ---------------------------------------------------------------------------
# REQ-995830 — K_UP + K_DOWN simultaneously: y unchanged (net zero)
# ---------------------------------------------------------------------------

class TestOppositeVerticalKeysCancel:
    """Pressing K_UP and K_DOWN simultaneously returns y unchanged (net zero y-delta)."""

    def test_up_and_down_together_y_unchanged(self):
        """REQ-995830: holding K_UP + K_DOWN simultaneously produces zero net y change."""
        adventure = _import_adventure()
        keys = _make_keys({273, 274})  # K_UP + K_DOWN
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50, (
            f"Expected y=50 (net zero) when K_UP+K_DOWN held, got {new_y}"
        )

    def test_up_and_down_together_x_unchanged(self):
        """REQ-995830: holding K_UP + K_DOWN does not affect x."""
        adventure = _import_adventure()
        keys = _make_keys({273, 274})
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50, (
            f"Expected x=50 unchanged when K_UP+K_DOWN held, got {new_x}"
        )


# ---------------------------------------------------------------------------
# REQ-A617E0 — K_LEFT + K_RIGHT simultaneously: x unchanged (net zero)
# ---------------------------------------------------------------------------

class TestOppositeHorizontalKeysCancel:
    """Pressing K_LEFT and K_RIGHT simultaneously returns x unchanged (net zero x-delta)."""

    def test_left_and_right_together_x_unchanged(self):
        """REQ-A617E0: holding K_LEFT + K_RIGHT simultaneously produces zero net x change."""
        adventure = _import_adventure()
        keys = _make_keys({275, 276})  # K_RIGHT + K_LEFT
        new_x, _ = adventure.move_player(50, 50, keys)
        assert new_x == 50, (
            f"Expected x=50 (net zero) when K_LEFT+K_RIGHT held, got {new_x}"
        )

    def test_left_and_right_together_y_unchanged(self):
        """REQ-A617E0: holding K_LEFT + K_RIGHT does not affect y."""
        adventure = _import_adventure()
        keys = _make_keys({275, 276})
        _, new_y = adventure.move_player(50, 50, keys)
        assert new_y == 50, (
            f"Expected y=50 unchanged when K_LEFT+K_RIGHT held, got {new_y}"
        )


# ---------------------------------------------------------------------------
# REQ-DEEA15 — run_game_loop calls pygame.key.get_pressed each frame
# ---------------------------------------------------------------------------

class TestRunGameLoopCallsGetPressed:
    """run_game_loop calls pygame.key.get_pressed each frame and passes result to move_player."""

    def test_run_game_loop_callable(self):
        """REQ-DEEA15: adventure module exposes a callable run_game_loop."""
        adventure = _import_adventure()
        assert callable(getattr(adventure, "run_game_loop", None)), (
            "run_game_loop not found or not callable in adventure module"
        )

    def test_get_pressed_called_during_game_loop(self):
        """REQ-DEEA15: pygame.key.get_pressed is called at least once per game-loop frame."""
        adventure = _import_adventure()

        # Minimal fake keys dict (no movement)
        fake_keys = _make_keys(set())

        # We need the loop to exit after one iteration; simulate a QUIT event.
        import pygame

        quit_event = MagicMock()
        quit_event.type = pygame.QUIT

        get_pressed_mock = MagicMock(return_value=fake_keys)

        with patch.object(pygame.key, "get_pressed", get_pressed_mock), \
             patch.object(pygame.event, "get", return_value=[quit_event]), \
             patch.object(pygame.display, "flip", MagicMock()), \
             patch.object(pygame.display, "update", MagicMock()):
            try:
                adventure.run_game_loop()
            except SystemExit:
                pass
            except Exception:
                # Any exit path is acceptable; we only care that get_pressed was called.
                pass

        assert get_pressed_mock.called, (
            "pygame.key.get_pressed was never called during run_game_loop"
        )

    def test_get_pressed_result_forwarded_to_move_player(self):
        """REQ-DEEA15: the dict returned by get_pressed is forwarded to move_player."""
        adventure = _import_adventure()

        fake_keys = _make_keys(set())
        import pygame

        quit_event = MagicMock()
        quit_event.type = pygame.QUIT

        get_pressed_mock = MagicMock(return_value=fake_keys)
        move_player_mock = MagicMock(return_value=(100, 100))

        with patch.object(pygame.key, "get_pressed", get_pressed_mock), \
             patch.object(pygame.event, "get", return_value=[quit_event]), \
             patch.object(pygame.display, "flip", MagicMock()), \
             patch.object(pygame.display, "update", MagicMock()), \
             patch.object(adventure, "move_player", move_player_mock):
            try:
                adventure.run_game_loop()
            except SystemExit:
                pass
            except Exception:
                pass

        # move_player must have been called with the keys dict returned by get_pressed.
        assert move_player_mock.called, (
            "move_player was never called from run_game_loop"
        )
        # Verify that at least one call forwarded the fake_keys dict.
        called_with_keys = any(
            fake_keys in call_args.args or fake_keys in call_args.kwargs.values()
            for call_args in move_player_mock.call_args_list
        )
        assert called_with_keys, (
            "move_player was called but not with the keys_pressed dict from get_pressed"
        )
