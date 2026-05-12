# bdb1c1b58ad0547a
# BAT-A1361E — Test environment setup verification
# REQ-33C367: SDL_VIDEODRIVER and SDL_AUDIODRIVER dummy env vars are set before pygame imports in conftest.py
# REQ-3857A0: requirements.txt pins exact versions of pygame and pytest

import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(
    "/Users/brandonshuey/data/ByteForge/Repositories/"
    "e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/fb4a5a61"
)


def test_conftest_sets_dummy_drivers():
    """REQ-33C367: SDL_VIDEODRIVER and SDL_AUDIODRIVER must be set to 'dummy'
    before any pygame import in conftest.py."""
    conftest_path = PROJECT_ROOT / "tests" / "conftest.py"

    assert conftest_path.exists(), (
        f"conftest.py not found at {conftest_path}. "
        "Create tests/conftest.py with SDL_VIDEODRIVER and SDL_AUDIODRIVER "
        "set to 'dummy' before importing pygame."
    )

    source = conftest_path.read_text(encoding="utf-8")

    # Parse into AST to inspect statement order
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise AssertionError(f"conftest.py has a syntax error: {exc}") from exc

    # Walk top-level statements to find the earliest pygame import and the
    # SDL env-var assignments, then assert ordering.
    first_pygame_import_lineno = None
    sdl_video_lineno = None
    sdl_audio_lineno = None

    for node in ast.walk(tree):
        # Detect: import pygame  or  from pygame import ...
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module = (
                node.names[0].name
                if isinstance(node, ast.Import)
                else (node.module or "")
            )
            if module.startswith("pygame"):
                lineno = node.lineno
                if first_pygame_import_lineno is None or lineno < first_pygame_import_lineno:
                    first_pygame_import_lineno = lineno

        # Detect: os.environ['SDL_VIDEODRIVER'] = 'dummy'
        #      or os.environ["SDL_VIDEODRIVER"] = "dummy"
        #      or os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
        if isinstance(node, (ast.Assign, ast.Expr)):
            node_src = ast.get_source_segment(source, node) or ""
            if "SDL_VIDEODRIVER" in node_src and "dummy" in node_src:
                if sdl_video_lineno is None or node.lineno < sdl_video_lineno:
                    sdl_video_lineno = node.lineno
            if "SDL_AUDIODRIVER" in node_src and "dummy" in node_src:
                if sdl_audio_lineno is None or node.lineno < sdl_audio_lineno:
                    sdl_audio_lineno = node.lineno

    assert sdl_video_lineno is not None, (
        "conftest.py does not set SDL_VIDEODRIVER to 'dummy'. "
        "Add: os.environ['SDL_VIDEODRIVER'] = 'dummy' before importing pygame."
    )
    assert sdl_audio_lineno is not None, (
        "conftest.py does not set SDL_AUDIODRIVER to 'dummy'. "
        "Add: os.environ['SDL_AUDIODRIVER'] = 'dummy' before importing pygame."
    )

    if first_pygame_import_lineno is not None:
        assert sdl_video_lineno < first_pygame_import_lineno, (
            f"SDL_VIDEODRIVER assignment (line {sdl_video_lineno}) must appear "
            f"before the first pygame import (line {first_pygame_import_lineno})."
        )
        assert sdl_audio_lineno < first_pygame_import_lineno, (
            f"SDL_AUDIODRIVER assignment (line {sdl_audio_lineno}) must appear "
            f"before the first pygame import (line {first_pygame_import_lineno})."
        )


def test_requirements_pins_versions():
    """REQ-3857A0: requirements.txt must pin exact versions of pygame and pytest
    using '==' specifiers."""
    req_path = PROJECT_ROOT / "requirements.txt"

    assert req_path.exists(), (
        f"requirements.txt not found at {req_path}. "
        "Create requirements.txt with pinned pygame== and pytest== entries."
    )

    content = req_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    pygame_pinned = any(
        re.match(r"^\s*pygame\s*==\s*\S+", line, re.IGNORECASE)
        for line in lines
    )
    pytest_pinned = any(
        re.match(r"^\s*pytest\s*==\s*\S+", line, re.IGNORECASE)
        for line in lines
    )

    assert pygame_pinned, (
        "requirements.txt does not contain a pinned pygame version. "
        "Add a line like: pygame==2.5.2"
    )
    assert pytest_pinned, (
        "requirements.txt does not contain a pinned pytest version. "
        "Add a line like: pytest==8.1.1"
    )
