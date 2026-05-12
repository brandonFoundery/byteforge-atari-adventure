import pygame

import adventure


def test_window_initializes_in_headless_mode():
    pygame.quit()
    adventure.initialize_pygame()
    try:
        surface = adventure.create_window(scale=3)
        assert surface.get_size() == (
            adventure.LOGICAL_WIDTH * 3,
            adventure.LOGICAL_HEIGHT * 3,
        )
    finally:
        pygame.quit()


def test_player_position_is_expected():
    expected_x = (adventure.LOGICAL_WIDTH - adventure.PLAYER_SIZE) // 2
    expected_y = (adventure.LOGICAL_HEIGHT - adventure.PLAYER_SIZE) // 2
    assert adventure.PLAYER_X == expected_x
    assert adventure.PLAYER_Y == expected_y


def test_main_loop_exits_on_escape_event():
    esc_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})

    pygame.quit()
    adventure.initialize_pygame()
    surface = adventure.create_window(scale=1)

    calls = {"count": 0}

    def fake_event_getter():
        calls["count"] += 1
        if calls["count"] == 1:
            return [esc_event]
        return []

    try:
        adventure.run_game_loop(surface, event_getter=fake_event_getter)
    finally:
        pygame.quit()

    assert calls["count"] >= 1
