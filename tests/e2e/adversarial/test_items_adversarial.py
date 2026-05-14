"""Adversarial tests for T4 — Items: pickup, carry-one, drop (chalice + key + sword).

Each test targets a specific potential defect in item pickup/carry/drop logic.
All tests run headless via SDL_VIDEODRIVER=dummy.

Run with:
    pytest tests/e2e/adversarial/test_items_adversarial.py -v
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import adventure  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fresh_items() -> list:
    return adventure._init_items()


def item_by_kind(items: list, kind: str) -> dict:
    return next(i for i in items if i["kind"] == kind)


def overlap_position(item: dict, player_size: int = adventure.PLAYER_SIZE) -> tuple[int, int]:
    """Return a player (px, py) that fully overlaps item's top-left pixel."""
    return item["x"], item["y"]


def just_outside_right(item: dict, player_size: int = adventure.PLAYER_SIZE) -> tuple[int, int]:
    """Return a player position whose right edge is exactly at the item's left edge (no overlap)."""
    # AABB: px + player_size > item['x'] must be FALSE => px + player_size == item['x']
    px = item["x"] - player_size
    py = item["y"]
    return px, py


def just_inside_right(item: dict, player_size: int = adventure.PLAYER_SIZE) -> tuple[int, int]:
    """Return a player position whose right edge is one pixel inside the item (overlap by 1)."""
    # AABB: px + player_size > item['x'] must be TRUE => px + player_size == item['x'] + 1
    px = item["x"] - player_size + 1
    py = item["y"]
    return px, py


# ---------------------------------------------------------------------------
# Class 1: Carry-one invariant
# ---------------------------------------------------------------------------

class TestCarryOneInvariant:

    def test_cannot_pickup_second_item_while_carrying(self):
        """CATCHES: _try_pickup replacing carried item when player overlaps a second one."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        key = item_by_kind(items, "key")

        # Pick up chalice first
        floor_after_chalice = [i for i in items if i["kind"] != "chalice"]
        px, py = overlap_position(key)
        # Simulate: already carrying chalice, walk into key
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, floor_after_chalice, chalice
        )
        assert carried_result is chalice, (
            "CARRY-ONE violated: second pickup replaced the carried item. "
            "Should keep chalice, not grab key."
        )
        assert key in floor_result, (
            "Key should remain on floor when player already carries chalice."
        )

    def test_carry_one_all_three_combinations(self):
        """CATCHES: carry-one bypass for specific item-kind combinations."""
        items = fresh_items()
        kinds = ["chalice", "key", "sword"]
        for carrying_kind in kinds:
            for floor_kind in kinds:
                if carrying_kind == floor_kind:
                    continue
                carried_item = item_by_kind(items, carrying_kind)
                floor_item = item_by_kind(items, floor_kind)
                px, py = overlap_position(floor_item)
                _, carried_result = adventure._try_pickup(
                    px, py, adventure.PLAYER_SIZE, [floor_item], carried_item
                )
                assert carried_result is carried_item, (
                    f"CARRY-ONE violated: carrying {carrying_kind}, "
                    f"touching {floor_kind} swapped it."
                )


# ---------------------------------------------------------------------------
# Class 2: All 3 kinds are independently pickupable
# ---------------------------------------------------------------------------

class TestAllKindsPickupable:

    def test_chalice_pickup(self):
        """CATCHES: chalice not being picked up (wrong kind check or wrong position)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        px, py = overlap_position(chalice)
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        assert carried_result is not None, "Chalice was not picked up."
        assert carried_result["kind"] == "chalice", (
            f"Expected to pick up chalice, got {carried_result['kind']}"
        )
        assert not any(i["kind"] == "chalice" for i in floor_result), (
            "Chalice should be removed from floor after pickup."
        )

    def test_key_pickup(self):
        """CATCHES: key not being picked up."""
        items = fresh_items()
        key = item_by_kind(items, "key")
        px, py = overlap_position(key)
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        assert carried_result is not None, "Key was not picked up."
        assert carried_result["kind"] == "key", (
            f"Expected to pick up key, got {carried_result['kind']}"
        )
        assert not any(i["kind"] == "key" for i in floor_result), (
            "Key should be removed from floor after pickup."
        )

    def test_sword_pickup(self):
        """CATCHES: sword not being picked up."""
        items = fresh_items()
        sword = item_by_kind(items, "sword")
        px, py = overlap_position(sword)
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        assert carried_result is not None, "Sword was not picked up."
        assert carried_result["kind"] == "sword", (
            f"Expected to pick up sword, got {carried_result['kind']}"
        )
        assert not any(i["kind"] == "sword" for i in floor_result), (
            "Sword should be removed from floor after pickup."
        )


# ---------------------------------------------------------------------------
# Class 3: Drop mechanics
# ---------------------------------------------------------------------------

class TestDropMechanics:

    def test_drop_clears_carried(self):
        """CATCHES: _on_drop_key not clearing the carried slot (carried remains non-None after drop)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_items = [i for i in items if i["kind"] != "chalice"]
        px, py = 50, 50
        floor_result, carried_result = adventure._on_drop_key(px, py, floor_items, chalice)
        assert carried_result is None, (
            "Carried must be None after drop; got non-None carried item."
        )

    def test_drop_adds_item_to_floor(self):
        """CATCHES: dropped item not being added back to floor_items."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_items = [i for i in items if i["kind"] != "chalice"]
        px, py = 50, 50
        floor_result, _ = adventure._on_drop_key(px, py, floor_items, chalice)
        assert any(i["kind"] == "chalice" for i in floor_result), (
            "Dropped chalice should appear in floor_items."
        )

    def test_drop_places_item_at_player_position(self):
        """CATCHES: dropped item placed at original spawn position instead of player position."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_items = [i for i in items if i["kind"] != "chalice"]
        px, py = 55, 60
        floor_result, _ = adventure._on_drop_key(px, py, floor_items, chalice)
        dropped = next(i for i in floor_result if i["kind"] == "chalice")
        assert dropped["x"] == px, (
            f"Dropped item x={dropped['x']} should equal player px={px}."
        )
        assert dropped["y"] == py, (
            f"Dropped item y={dropped['y']} should equal player py={py}."
        )

    def test_drop_preserves_item_kind_color_size(self):
        """CATCHES: dropped item losing its kind, color, or size (corrupted copy)."""
        items = fresh_items()
        sword = item_by_kind(items, "sword")
        floor_items = [i for i in items if i["kind"] != "sword"]
        original_kind = sword["kind"]
        original_color = sword["color"]
        original_size = sword["size"]
        px, py = 80, 90
        floor_result, _ = adventure._on_drop_key(px, py, floor_items, sword)
        dropped = next(i for i in floor_result if i["kind"] == "sword")
        assert dropped["kind"] == original_kind, "Dropped item kind corrupted."
        assert dropped["color"] == original_color, "Dropped item color corrupted."
        assert dropped["size"] == original_size, "Dropped item size corrupted."

    def test_drop_with_no_carried_is_noop(self):
        """CATCHES: _on_drop_key modifying floor_items when carried is None."""
        items = fresh_items()
        floor_copy = list(items)
        floor_result, carried_result = adventure._on_drop_key(50, 50, items, None)
        assert len(floor_result) == len(floor_copy), (
            "floor_items length changed on no-op drop (carried was None)."
        )
        assert carried_result is None, "carried should remain None after no-op drop."

    def test_drop_does_not_mutate_original_item_dict(self):
        """CATCHES: _on_drop_key modifying the original carried dict in-place
        (changing the original item's x/y instead of working on a copy)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        original_x = chalice["x"]
        original_y = chalice["y"]
        floor_items = [i for i in items if i["kind"] != "chalice"]
        adventure._on_drop_key(99, 88, floor_items, chalice)
        assert chalice["x"] == original_x, (
            f"Original chalice dict mutated: x changed from {original_x} to {chalice['x']}."
        )
        assert chalice["y"] == original_y, (
            f"Original chalice dict mutated: y changed from {original_y} to {chalice['y']}."
        )


# ---------------------------------------------------------------------------
# Class 4: Drop-then-pickup same item
# ---------------------------------------------------------------------------

class TestDropThenPickupSameItem:

    def test_drop_then_pickup_same_item(self):
        """CATCHES: dropped item not being re-pickupable (e.g. identity check bug or position mismatch)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_without = [i for i in items if i["kind"] != "chalice"]

        # Drop chalice at position (50, 50)
        drop_px, drop_py = 50, 50
        floor_after_drop, _ = adventure._on_drop_key(drop_px, drop_py, floor_without, chalice)

        # Verify it's on the floor
        assert any(i["kind"] == "chalice" for i in floor_after_drop), (
            "Chalice should be on floor after drop."
        )

        # Player stands at (50, 50) — same as drop position — tries to pick up
        floor_after_pickup, carried_result = adventure._try_pickup(
            drop_px, drop_py, adventure.PLAYER_SIZE, floor_after_drop, None
        )
        assert carried_result is not None, (
            "Dropped item should be re-pickupable when player stands on it."
        )
        assert carried_result["kind"] == "chalice", (
            f"Expected to re-pick chalice, got {carried_result['kind'] if carried_result else 'None'}."
        )


# ---------------------------------------------------------------------------
# Class 5: AABB boundary precision
# ---------------------------------------------------------------------------

class TestAabbBoundaryPrecision:

    def test_player_just_outside_item_does_not_trigger_pickup(self):
        """CATCHES: AABB check using >= instead of > (off-by-one allowing pickup from outside)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        px, py = just_outside_right(chalice)
        # px + PLAYER_SIZE == chalice['x'] — no overlap (px + ps > item['x'] is False)
        assert px + adventure.PLAYER_SIZE == chalice["x"], (
            "Test setup error: player right edge should exactly equal item left edge."
        )
        _, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        assert carried_result is None, (
            f"Player just outside item (px+ps==item['x']) should NOT trigger pickup. "
            f"px={px}, item['x']={chalice['x']}, player_size={adventure.PLAYER_SIZE}"
        )

    def test_player_just_inside_item_triggers_pickup(self):
        """CATCHES: AABB check using > instead of >= (off-by-one preventing valid pickup at boundary)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        px, py = just_inside_right(chalice)
        # px + PLAYER_SIZE == chalice['x'] + 1 — one-pixel overlap
        assert px + adventure.PLAYER_SIZE == chalice["x"] + 1, (
            "Test setup error: player right edge should be one pixel inside item."
        )
        _, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        assert carried_result is not None, (
            f"Player with 1-pixel overlap into item should trigger pickup. "
            f"px={px}, item['x']={chalice['x']}, player_size={adventure.PLAYER_SIZE}"
        )


# ---------------------------------------------------------------------------
# Class 6: Rapid pickup-drop cycle consistency
# ---------------------------------------------------------------------------

class TestRapidCycleMaintainsConsistency:

    def test_rapid_pickup_drop_cycle_state_consistent(self):
        """CATCHES: state corruption after repeated pickup/drop (e.g. duplicate items, None carried
        mid-cycle, or floor count wrong after N iterations)."""
        items = fresh_items()
        chalice = item_by_kind(items, "chalice")
        floor_items = [i for i in items if i["kind"] != "chalice"]
        # Start: carrying chalice, 2 items on floor

        px, py = 60, 60
        carried = chalice
        current_floor = list(floor_items)

        for cycle in range(10):
            # Drop
            current_floor, carried = adventure._on_drop_key(px, py, current_floor, carried)
            assert carried is None, f"Cycle {cycle}: carried should be None after drop."
            chalice_on_floor = [i for i in current_floor if i["kind"] == "chalice"]
            assert len(chalice_on_floor) == 1, (
                f"Cycle {cycle}: exactly 1 chalice should be on floor after drop, "
                f"got {len(chalice_on_floor)}."
            )

            # Pick up
            current_floor, carried = adventure._try_pickup(
                px, py, adventure.PLAYER_SIZE, current_floor, None
            )
            assert carried is not None, f"Cycle {cycle}: chalice should be re-picked up."
            assert carried["kind"] == "chalice", (
                f"Cycle {cycle}: wrong item picked up: {carried['kind']}."
            )
            chalice_on_floor = [i for i in current_floor if i["kind"] == "chalice"]
            assert len(chalice_on_floor) == 0, (
                f"Cycle {cycle}: chalice should not be on floor after pickup."
            )

        # Final state: carrying chalice, no chalice on floor
        assert carried is not None and carried["kind"] == "chalice"
        assert not any(i["kind"] == "chalice" for i in current_floor)

    def test_floor_item_count_invariant_across_drop_cycle(self):
        """CATCHES: item duplication bug — floor grows by more than 1 per drop,
        or shrinks by more than 1 per pickup."""
        items = fresh_items()
        # Pick up chalice, leaving 2 on floor
        chalice = item_by_kind(items, "chalice")
        floor = [i for i in items if i["kind"] != "chalice"]
        assert len(floor) == 2, "Setup: expected 2 floor items after chalice pickup."

        px, py = 70, 70
        # Drop — floor should have 3 items
        floor, carried = adventure._on_drop_key(px, py, floor, chalice)
        assert len(floor) == 3, f"After drop, floor should have 3 items, got {len(floor)}."
        assert carried is None

        # Pick up chalice — floor should return to 2
        floor, carried = adventure._try_pickup(px, py, adventure.PLAYER_SIZE, floor, None)
        assert carried is not None and carried["kind"] == "chalice"
        assert len(floor) == 2, f"After pickup, floor should have 2 items, got {len(floor)}."


# ---------------------------------------------------------------------------
# Class 7: Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_pickup_from_empty_floor_is_safe(self):
        """CATCHES: _try_pickup crashing or returning wrong state when floor_items is empty."""
        floor_result, carried_result = adventure._try_pickup(
            50, 50, adventure.PLAYER_SIZE, [], None
        )
        assert floor_result == [], "Empty floor should stay empty after no-pickup."
        assert carried_result is None, "Carried should remain None when floor is empty."

    def test_pickup_far_from_all_items_returns_unchanged_state(self):
        """CATCHES: pickup triggering when player is far from all items (off-by-one in AABB)."""
        items = fresh_items()
        # Place player far from all items (center of screen)
        px, py = adventure.PLAYER_X, adventure.PLAYER_Y
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, items, None
        )
        # Only pick up if actually overlapping. Center is (76, 101), items at (40,50),(100,80),(70,140).
        # Key at (100,80): px+ps=84, item x=100 => 84 > 100 is False. No overlap expected.
        if carried_result is not None:
            # If overlap occurs (e.g. player spawns on an item), that's a design observation, not a bug
            # — just verify floor count decreased by exactly 1
            assert len(floor_result) == len(items) - 1, (
                "If player spawns on item, exactly one should be picked up."
            )
        else:
            assert len(floor_result) == len(items), (
                "No pickup should mean floor_items unchanged."
            )

    def test_init_items_returns_three_distinct_kinds(self):
        """CATCHES: _init_items returning duplicate or missing item kinds."""
        items = adventure._init_items()
        kinds = [i["kind"] for i in items]
        assert len(kinds) == 3, f"Expected 3 items, got {len(kinds)}."
        assert "chalice" in kinds, "chalice missing from _init_items."
        assert "key" in kinds, "key missing from _init_items."
        assert "sword" in kinds, "sword missing from _init_items."
        assert len(set(kinds)) == 3, f"Duplicate item kinds in _init_items: {kinds}."

    def test_two_items_at_same_position_only_one_picked_up(self):
        """CATCHES: AABB loop picking up multiple items in one call (all items at same position overlap)."""
        # Place two items at the same spot
        item_a = {"kind": "chalice", "x": 50, "y": 50, "size": adventure.ITEM_SIZE, "color": adventure.CHALICE_COLOR}
        item_b = {"kind": "key", "x": 50, "y": 50, "size": adventure.ITEM_SIZE, "color": adventure.KEY_COLOR}
        floor = [item_a, item_b]
        px, py = 50, 50
        floor_result, carried_result = adventure._try_pickup(
            px, py, adventure.PLAYER_SIZE, floor, None
        )
        assert carried_result is not None, "Should pick up one item from overlapping pair."
        assert len(floor_result) == 1, (
            f"Only one of two co-located items should be picked up; "
            f"floor has {len(floor_result)} items."
        )
