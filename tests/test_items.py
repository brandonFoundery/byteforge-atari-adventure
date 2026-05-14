"""
Tests for item rendering and draw call ordering in adventure.py.

Covers:
- REQ-41DE94: draw_items called before draw_player in main loop
- REQ-6A9EA5: main loop calls draw_items after draw_room and before draw_player each frame
- REQ-8026FA: pixel near player position matches carried item color after pickup
- REQ-FCB527: pixel at floor item position matches item color before pickup
- REQ-FA59D1: pixel at original world position is empty after pickup
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import adventure  # noqa: E402

pygame.init()

SURFACE_W = adventure.LOGICAL_WIDTH
SURFACE_H = adventure.LOGICAL_HEIGHT


def make_surface() -> pygame.Surface:
    surf = pygame.Surface((SURFACE_W, SURFACE_H))
    surf.fill((0, 0, 0))
    return surf


def pixel_at(surface: pygame.Surface, x: int, y: int) -> tuple:
    return surface.get_at((x, y))[:3]


def fresh_items() -> list:
    return adventure._init_items()


def item_by_kind(items: list, kind: str) -> dict:
    return next(i for i in items if i["kind"] == kind)


def _make_quit_event_getter():
    called = [False]

    def getter():
        if not called[0]:
            called[0] = True
            quit_event = pygame.event.Event(pygame.QUIT)
            return [quit_event]
        return []

    return getter


# ---------------------------------------------------------------------------
# REQ-41DE94 & REQ-6A9EA5 — draw call order in main loop
# ---------------------------------------------------------------------------

class TestDrawCallOrder:
    """draw_items must be called after draw_room and before draw_player each frame."""

    def setup_method(self):
        if not pygame.get_init():
            pygame.init()

    def test_draw_order_room_items_player(self):
        surface = pygame.Surface((SURFACE_W, SURFACE_H))
        call_log = []

        original_draw_room = adventure.draw_room
        original_draw_items = adventure.draw_items
        original_draw_player = adventure.draw_player

        def mock_draw_room(s):
            call_log.append("draw_room")
            return original_draw_room(s)

        def mock_draw_items(s, fi, c, px, py):
            call_log.append("draw_items")
            return original_draw_items(s, fi, c, px, py)

        def mock_draw_player(s, x=adventure.PLAYER_X, y=adventure.PLAYER_Y):
            call_log.append("draw_player")
            return original_draw_player(s, x, y)

        with patch.object(adventure, "draw_room", side_effect=mock_draw_room), \
             patch.object(adventure, "draw_items", side_effect=mock_draw_items), \
             patch.object(adventure, "draw_player", side_effect=mock_draw_player):
            adventure.run_game_loop(
                surface,
                fps=1,
                event_getter=_make_quit_event_getter(),
            )

        room_idx = call_log.index("draw_room")
        items_idx = call_log.index("draw_items")
        player_idx = call_log.index("draw_player")
        assert room_idx < items_idx < player_idx, (
            f"Expected draw_room({room_idx}) < draw_items({items_idx}) < draw_player({player_idx})"
        )


# ---------------------------------------------------------------------------
# REQ-FCB527 — pixel at floor item matches color before pickup
# ---------------------------------------------------------------------------

class TestPixelMatchesColorBeforePickup:

    def test_chalice_visible_before_pickup(self):
        surf = make_surface()
        items = fresh_items()
        adventure.draw_items(surf, items, None, adventure.PLAYER_X, adventure.PLAYER_Y)
        chalice = item_by_kind(items, "chalice")
        assert pixel_at(surf, chalice["x"], chalice["y"]) == chalice["color"]

    def test_key_visible_before_pickup(self):
        surf = make_surface()
        items = fresh_items()
        adventure.draw_items(surf, items, None, adventure.PLAYER_X, adventure.PLAYER_Y)
        key = item_by_kind(items, "key")
        assert pixel_at(surf, key["x"], key["y"]) == key["color"]

    def test_sword_visible_before_pickup(self):
        surf = make_surface()
        items = fresh_items()
        adventure.draw_items(surf, items, None, adventure.PLAYER_X, adventure.PLAYER_Y)
        sword = item_by_kind(items, "sword")
        assert pixel_at(surf, sword["x"], sword["y"]) == sword["color"]


# ---------------------------------------------------------------------------
# REQ-8026FA — pixel near player matches carried item color after pickup
# ---------------------------------------------------------------------------

class TestPixelNearPlayerMatchesCarriedColorAfterPickup:

    def test_chalice_color_at_player_offset_after_pickup(self):
        surf = make_surface()
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_after = [i for i in items if i["kind"] != "chalice"]
        px, py = 50, 60
        adventure.draw_items(surf, floor_after, chalice, px, py)
        assert pixel_at(surf, px + adventure.PLAYER_SIZE, py) == chalice["color"]

    def test_key_color_at_player_offset_after_pickup(self):
        surf = make_surface()
        items = fresh_items()
        key = item_by_kind(items, "key")
        floor_after = [i for i in items if i["kind"] != "key"]
        px, py = 60, 70
        adventure.draw_items(surf, floor_after, key, px, py)
        assert pixel_at(surf, px + adventure.PLAYER_SIZE, py) == key["color"]

    def test_sword_color_at_player_offset_after_pickup(self):
        surf = make_surface()
        items = fresh_items()
        sword = item_by_kind(items, "sword")
        floor_after = [i for i in items if i["kind"] != "sword"]
        px, py = 40, 50
        adventure.draw_items(surf, floor_after, sword, px, py)
        assert pixel_at(surf, px + adventure.PLAYER_SIZE, py) == sword["color"]


# ---------------------------------------------------------------------------
# REQ-FA59D1 — pixel at old world position empty after pickup
# ---------------------------------------------------------------------------

class TestPixelAtOldPositionEmptyAfterPickup:

    def test_chalice_old_position_empty_after_pickup(self):
        surf = make_surface()
        chalice = {"kind": "chalice", "x": adventure.CHALICE_X, "y": adventure.CHALICE_Y,
                   "size": adventure.ITEM_SIZE, "color": adventure.CHALICE_COLOR}
        px, py = 10, 10
        adventure.draw_items(surf, [], chalice, px, py)
        assert pixel_at(surf, adventure.CHALICE_X, adventure.CHALICE_Y) != adventure.CHALICE_COLOR

    def test_key_old_position_empty_after_pickup(self):
        surf = make_surface()
        key = {"kind": "key", "x": adventure.KEY_X, "y": adventure.KEY_Y,
               "size": adventure.ITEM_SIZE, "color": adventure.KEY_COLOR}
        px, py = 10, 10
        adventure.draw_items(surf, [], key, px, py)
        assert pixel_at(surf, adventure.KEY_X, adventure.KEY_Y) != adventure.KEY_COLOR

    def test_sword_old_position_empty_after_pickup(self):
        surf = make_surface()
        sword = {"kind": "sword", "x": adventure.SWORD_X, "y": adventure.SWORD_Y,
                 "size": adventure.ITEM_SIZE, "color": adventure.SWORD_COLOR}
        px, py = 10, 10
        adventure.draw_items(surf, [], sword, px, py)
        assert pixel_at(surf, adventure.SWORD_X, adventure.SWORD_Y) != adventure.SWORD_COLOR

    def test_before_after_pickup_transition(self):
        surf_before = make_surface()
        items = fresh_items()
        adventure.draw_items(surf_before, items, None, adventure.PLAYER_X, adventure.PLAYER_Y)
        chalice = item_by_kind(items, "chalice")
        assert pixel_at(surf_before, chalice["x"], chalice["y"]) == chalice["color"]

        surf_after = make_surface()
        floor_after = [i for i in items if i["kind"] != "chalice"]
        px, py = 10, 10
        adventure.draw_items(surf_after, floor_after, chalice, px, py)
        assert pixel_at(surf_after, chalice["x"], chalice["y"]) != chalice["color"]
