"""Tests for player movement (C01): PLAYER_SPEED constant and move_player function."""

import pygame
import pytest

import adventure

# Boundary constants derived from production values
X_MIN = adventure.WALL_THICKNESS
X_MAX = adventure.LOGICAL_WIDTH - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE
Y_MIN = adventure.WALL_THICKNESS
Y_MAX = adventure.LOGICAL_HEIGHT - adventure.WALL_THICKNESS - adventure.PLAYER_SIZE

CENTER_X = adventure.PLAYER_X
CENTER_Y = adventure.PLAYER_Y


def no_keys():
    return {
        pygame.K_RIGHT: False,
        pygame.K_LEFT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False,
    }


def keys_with(key):
    k = no_keys()
    k[key] = True
    return k


def test_player_speed_constant_defined():
    assert hasattr(adventure, "PLAYER_SPEED")
    assert isinstance(adventure.PLAYER_SPEED, int)
    assert adventure.PLAYER_SPEED > 0


def test_move_right_increases_x():
    x, y = adventure.move_player(CENTER_X, CENTER_Y, keys_with(pygame.K_RIGHT))
    assert x == CENTER_X + adventure.PLAYER_SPEED
    assert y == CENTER_Y


def test_move_left_decreases_x():
    x, y = adventure.move_player(CENTER_X, CENTER_Y, keys_with(pygame.K_LEFT))
    assert x == CENTER_X - adventure.PLAYER_SPEED
    assert y == CENTER_Y


def test_move_up_decreases_y():
    x, y = adventure.move_player(CENTER_X, CENTER_Y, keys_with(pygame.K_UP))
    assert x == CENTER_X
    assert y == CENTER_Y - adventure.PLAYER_SPEED


def test_move_down_increases_y():
    x, y = adventure.move_player(CENTER_X, CENTER_Y, keys_with(pygame.K_DOWN))
    assert x == CENTER_X
    assert y == CENTER_Y + adventure.PLAYER_SPEED


def test_wall_clamp_left():
    x, y = adventure.move_player(X_MIN, CENTER_Y, keys_with(pygame.K_LEFT))
    assert x == X_MIN


def test_wall_clamp_right():
    x, y = adventure.move_player(X_MAX, CENTER_Y, keys_with(pygame.K_RIGHT))
    assert x == X_MAX


def test_wall_clamp_top():
    x, y = adventure.move_player(CENTER_X, Y_MIN, keys_with(pygame.K_UP))
    assert y == Y_MIN


def test_wall_clamp_bottom():
    x, y = adventure.move_player(CENTER_X, Y_MAX, keys_with(pygame.K_DOWN))
    assert y == Y_MAX


def test_no_keys_pressed_position_unchanged():
    x, y = adventure.move_player(CENTER_X, CENTER_Y, no_keys())
    assert x == CENTER_X
    assert y == CENTER_Y
