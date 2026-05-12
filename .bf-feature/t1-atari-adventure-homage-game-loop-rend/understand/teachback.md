# Teachback

Feature slug: t1-atari-adventure-homage-game-loop-rend  
Witness: bdb1c1b58ad0547a

This understand scope is a tight T1 baseline: build one pygame script in `adventure.py`, render one fixed room with walls and a centered player square, hold the loop near 30 FPS, and exit on ESC or OS close.

Location grounding from `location.yaml`:
- `README.md` is in scope for command documentation updates.
- `adventure.py` is the only game implementation file.
- `tests/test_adventure.py` carries ticket-required behavior checks.
- `tests/conftest.py` sets SDL dummy drivers before pygame import.
- `requirements.txt` pins the two dependencies for deterministic setup.

Risk grounding from `impact.yaml`:
- `adventure.py` has a high-severity `loop-timing` risk: bad event polling or frame pacing can stall exit behavior or destabilize FPS.
- `tests/conftest.py` has a medium-severity `test-environment` risk: late SDL dummy setup can break headless runs.

Success criteria (verbatim from `intent.yaml`):
- Running `python adventure.py` opens one pygame window at about 160x210 logical pixels scaled 3x to 4x.
- The room background is a single solid color.
- Four wall rectangles render around the full perimeter with no passage gaps.
- A small player square renders near the room center at deterministic coordinates.
- The main loop ticks at about 30 FPS.
- ESC key press or OS close event exits the process cleanly with pygame teardown.
- Pytest coverage includes headless initialization, expected player coordinates, and ESC-driven loop exit.

Out of scope remains movement, multi-room traversal, and item/dragon/win systems for later tickets.
