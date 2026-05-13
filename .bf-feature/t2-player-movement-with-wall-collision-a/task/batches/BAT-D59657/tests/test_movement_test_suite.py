"""
MovementTestSuite — verifies that the test infrastructure for T2 player movement
works correctly by running pytest as a subprocess and inspecting results.

Witness: b6731a13a9b00140
Batch:   BAT-D59657
Feature: t2-player-movement-with-wall-collision-a

REQs covered:
  REQ-14E1B4  all 10 tests in tests/test_movement.py pass with zero skips/xfails
  REQ-900635  pytest collects exactly 10 tests from tests/test_movement.py
  REQ-4D064A  test_movement.py verifies each of the four wall clamp boundaries
  REQ-BE9F8B  test_movement.py verifies each of the four directional axes
  REQ-7CE888  pytest collects and passes all tests in tests/test_adventure.py
  REQ-E37D72  tests/conftest.py sets SDL_VIDEODRIVER=dummy
  REQ-146585  test_main_loop_exits_on_escape_event passes after T2 changes
  REQ-ADA63A  pygame.key.get_pressed is callable inside run_game_loop with dummy driver
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Absolute path to the project root (two levels up from this file's location at
# .bf-feature/.../tests/test_movement_test_suite.py)
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[6]  # worktree root
TESTS_DIR = PROJECT_ROOT / "tests"


def _run_pytest(*extra_args: str, cwd: Path = PROJECT_ROOT) -> subprocess.CompletedProcess:
    """Run pytest as a subprocess and return the CompletedProcess."""
    cmd = [
        sys.executable, "-m", "pytest",
        "--tb=short",
        "-v",
        *extra_args,
    ]
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
    )


def _parse_summary(output: str) -> dict:
    """
    Parse pytest's terminal summary line such as:
      "5 passed, 2 failed, 1 skipped, 1 xfailed in 0.12s"
    Returns a dict with keys: passed, failed, skipped, xfailed, errors (all int).
    """
    summary = {k: 0 for k in ("passed", "failed", "skipped", "xfailed", "errors")}
    # Match the "N passed" / "N failed" / … tokens anywhere in the summary line
    for key in summary:
        m = re.search(rf"(\d+)\s+{key}", output)
        if m:
            summary[key] = int(m.group(1))
    return summary


def _collect_test_ids(target_path: str, cwd: Path = PROJECT_ROOT) -> list[str]:
    """Return the list of test node IDs pytest would collect."""
    cmd = [
        sys.executable, "-m", "pytest",
        "--collect-only", "-q",
        target_path,
    ]
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
    )
    # Lines that represent collected tests look like "tests/file.py::test_name"
    ids = [
        line.strip()
        for line in result.stdout.splitlines()
        if "::" in line and not line.startswith("=")
    ]
    return ids


# ---------------------------------------------------------------------------
# REQ-900635 — pytest collects exactly 10 tests from tests/test_movement.py
# ---------------------------------------------------------------------------

class TestCollectionCount:
    def test_movement_file_collects_exactly_10_tests(self):
        """REQ-900635: pytest must collect exactly 10 tests from test_movement.py."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert len(ids) == 10, (
            f"Expected exactly 10 collected tests from tests/test_movement.py, "
            f"got {len(ids)}: {ids}"
        )


# ---------------------------------------------------------------------------
# REQ-14E1B4 — all 10 tests pass with zero skips and zero xfails
# ---------------------------------------------------------------------------

class TestMovementPassRate:
    def test_all_movement_tests_pass(self):
        """REQ-14E1B4: all 10 tests must pass."""
        result = _run_pytest("tests/test_movement.py")
        summary = _parse_summary(result.stdout + result.stderr)
        assert summary["passed"] == 10, (
            f"Expected 10 passed, got {summary['passed']}.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_no_skips_in_movement_suite(self):
        """REQ-14E1B4: zero skipped tests."""
        result = _run_pytest("tests/test_movement.py")
        summary = _parse_summary(result.stdout + result.stderr)
        assert summary["skipped"] == 0, (
            f"Expected 0 skipped, got {summary['skipped']}.\n"
            f"stdout:\n{result.stdout}"
        )

    def test_no_xfails_in_movement_suite(self):
        """REQ-14E1B4: zero xfailed tests."""
        result = _run_pytest("tests/test_movement.py")
        summary = _parse_summary(result.stdout + result.stderr)
        assert summary["xfailed"] == 0, (
            f"Expected 0 xfailed, got {summary['xfailed']}.\n"
            f"stdout:\n{result.stdout}"
        )

    def test_movement_suite_exit_code_is_zero(self):
        """REQ-14E1B4: pytest exit code must be 0 (all pass)."""
        result = _run_pytest("tests/test_movement.py")
        assert result.returncode == 0, (
            f"pytest exited with code {result.returncode}.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


# ---------------------------------------------------------------------------
# REQ-4D064A — test_movement.py verifies each of the four wall clamp boundaries
# ---------------------------------------------------------------------------

class TestWallClampCoverage:
    CLAMP_TEST_NAMES = [
        "test_wall_clamp_left",
        "test_wall_clamp_right",
        "test_wall_clamp_top",
        "test_wall_clamp_bottom",
    ]

    def test_wall_clamp_left_is_collected(self):
        """REQ-4D064A: test_wall_clamp_left must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_wall_clamp_left" in i for i in ids), (
            f"test_wall_clamp_left not found in collected IDs: {ids}"
        )

    def test_wall_clamp_right_is_collected(self):
        """REQ-4D064A: test_wall_clamp_right must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_wall_clamp_right" in i for i in ids), (
            f"test_wall_clamp_right not found in collected IDs: {ids}"
        )

    def test_wall_clamp_top_is_collected(self):
        """REQ-4D064A: test_wall_clamp_top must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_wall_clamp_top" in i for i in ids), (
            f"test_wall_clamp_top not found in collected IDs: {ids}"
        )

    def test_wall_clamp_bottom_is_collected(self):
        """REQ-4D064A: test_wall_clamp_bottom must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_wall_clamp_bottom" in i for i in ids), (
            f"test_wall_clamp_bottom not found in collected IDs: {ids}"
        )

    def test_all_four_clamp_tests_pass(self):
        """REQ-4D064A: all four wall-clamp tests must pass."""
        for name in self.CLAMP_TEST_NAMES:
            result = _run_pytest(f"tests/test_movement.py::{name}")
            assert result.returncode == 0, (
                f"{name} failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


# ---------------------------------------------------------------------------
# REQ-BE9F8B — test_movement.py verifies each of the four directional axes
# ---------------------------------------------------------------------------

class TestDirectionalAxisCoverage:
    DIRECTION_TEST_NAMES = [
        "test_move_right_increases_x",
        "test_move_left_decreases_x",
        "test_move_up_decreases_y",
        "test_move_down_increases_y",
    ]

    def test_move_right_is_collected(self):
        """REQ-BE9F8B: test_move_right_increases_x must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_move_right_increases_x" in i for i in ids), (
            f"test_move_right_increases_x not found in collected IDs: {ids}"
        )

    def test_move_left_is_collected(self):
        """REQ-BE9F8B: test_move_left_decreases_x must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_move_left_decreases_x" in i for i in ids), (
            f"test_move_left_decreases_x not found in collected IDs: {ids}"
        )

    def test_move_up_is_collected(self):
        """REQ-BE9F8B: test_move_up_decreases_y must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_move_up_decreases_y" in i for i in ids), (
            f"test_move_up_decreases_y not found in collected IDs: {ids}"
        )

    def test_move_down_is_collected(self):
        """REQ-BE9F8B: test_move_down_increases_y must be collected."""
        ids = _collect_test_ids("tests/test_movement.py")
        assert any("test_move_down_increases_y" in i for i in ids), (
            f"test_move_down_increases_y not found in collected IDs: {ids}"
        )

    def test_all_four_direction_tests_pass(self):
        """REQ-BE9F8B: all four directional tests must pass."""
        for name in self.DIRECTION_TEST_NAMES:
            result = _run_pytest(f"tests/test_movement.py::{name}")
            assert result.returncode == 0, (
                f"{name} failed.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


# ---------------------------------------------------------------------------
# REQ-7CE888 — pytest collects and passes all tests in tests/test_adventure.py
# ---------------------------------------------------------------------------

class TestAdventureTestSuite:
    def test_adventure_suite_has_at_least_three_tests(self):
        """REQ-7CE888: test_adventure.py must have at least 3 collected tests."""
        ids = _collect_test_ids("tests/test_adventure.py")
        assert len(ids) >= 3, (
            f"Expected at least 3 tests in test_adventure.py, got {len(ids)}: {ids}"
        )

    def test_adventure_suite_exit_code_is_zero(self):
        """REQ-7CE888: entire test_adventure.py must pass (exit code 0)."""
        result = _run_pytest("tests/test_adventure.py")
        assert result.returncode == 0, (
            f"test_adventure.py failed (exit {result.returncode}).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_adventure_suite_no_failures(self):
        """REQ-7CE888: zero failing tests in test_adventure.py."""
        result = _run_pytest("tests/test_adventure.py")
        summary = _parse_summary(result.stdout + result.stderr)
        assert summary["failed"] == 0, (
            f"Expected 0 failures in test_adventure.py, got {summary['failed']}.\n"
            f"stdout:\n{result.stdout}"
        )


# ---------------------------------------------------------------------------
# REQ-E37D72 — tests/conftest.py sets SDL_VIDEODRIVER=dummy
# ---------------------------------------------------------------------------

class TestConftestSdlEnv:
    def test_conftest_sets_sdl_videodriver_dummy(self):
        """REQ-E37D72: conftest.py must contain SDL_VIDEODRIVER = dummy assignment."""
        conftest = TESTS_DIR / "conftest.py"
        assert conftest.exists(), f"tests/conftest.py not found at {conftest}"
        content = conftest.read_text()
        assert "SDL_VIDEODRIVER" in content, (
            "tests/conftest.py does not set SDL_VIDEODRIVER"
        )
        assert "dummy" in content, (
            "tests/conftest.py does not assign 'dummy' to SDL_VIDEODRIVER"
        )

    def test_conftest_sets_sdl_audiodriver_dummy(self):
        """REQ-E37D72: conftest.py should also silence audio (SDL_AUDIODRIVER=dummy)."""
        conftest = TESTS_DIR / "conftest.py"
        assert conftest.exists(), f"tests/conftest.py not found at {conftest}"
        content = conftest.read_text()
        assert "SDL_AUDIODRIVER" in content, (
            "tests/conftest.py does not set SDL_AUDIODRIVER"
        )

    def test_movement_tests_run_headlessly_via_conftest(self):
        """REQ-E37D72: movement tests can run without a display (conftest provides dummy driver)."""
        # If conftest properly sets the env var, test_movement.py will not crash with
        # "No available video device" — we verify by a clean subprocess that inherits
        # NO SDL_VIDEODRIVER from the parent environment.
        env = {k: v for k, v in os.environ.items() if "SDL" not in k}
        cmd = [sys.executable, "-m", "pytest", "--tb=short", "-q", "tests/test_movement.py"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
        )
        assert result.returncode == 0, (
            f"Movement tests failed when run without explicit SDL env vars "
            f"(conftest should supply them).\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


# ---------------------------------------------------------------------------
# REQ-146585 — test_main_loop_exits_on_escape_event passes after T2 changes
# ---------------------------------------------------------------------------

class TestEscapeEventLoop:
    def test_escape_event_test_is_collected(self):
        """REQ-146585: test_main_loop_exits_on_escape_event must be collected."""
        ids = _collect_test_ids("tests/test_adventure.py")
        assert any("test_main_loop_exits_on_escape_event" in i for i in ids), (
            f"test_main_loop_exits_on_escape_event not found in: {ids}"
        )

    def test_escape_event_test_passes(self):
        """REQ-146585: test_main_loop_exits_on_escape_event must pass."""
        result = _run_pytest(
            "tests/test_adventure.py::test_main_loop_exits_on_escape_event"
        )
        assert result.returncode == 0, (
            f"test_main_loop_exits_on_escape_event failed.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


# ---------------------------------------------------------------------------
# REQ-ADA63A — pygame.key.get_pressed is callable inside run_game_loop
# ---------------------------------------------------------------------------

class TestGetPressedCallable:
    def test_run_game_loop_invokes_get_pressed(self):
        """
        REQ-ADA63A: run_game_loop must call pygame.key.get_pressed each frame.
        We verify this by confirming that test_main_loop_exits_on_escape_event passes
        with SDL_VIDEODRIVER=dummy (if get_pressed raised, the test would fail).
        """
        result = _run_pytest(
            "tests/test_adventure.py::test_main_loop_exits_on_escape_event"
        )
        assert result.returncode == 0, (
            f"run_game_loop appears to fail when get_pressed is called under dummy driver.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    def test_get_pressed_does_not_raise_with_dummy_driver(self):
        """
        REQ-ADA63A: pygame.key.get_pressed must not raise under SDL_VIDEODRIVER=dummy.
        We run a tiny inline script to prove it.
        """
        script = (
            "import os; os.environ['SDL_VIDEODRIVER']='dummy'; "
            "os.environ['SDL_AUDIODRIVER']='dummy'; "
            "import pygame; pygame.init(); "
            "result = pygame.key.get_pressed(); "
            "assert len(result) > 0, 'get_pressed returned empty'; "
            "pygame.quit()"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"pygame.key.get_pressed raised with SDL_VIDEODRIVER=dummy.\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
