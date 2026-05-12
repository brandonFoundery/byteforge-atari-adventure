# bdb1c1b58ad0547a
# REQ-95C535: README documents install, run, and test commands verbatim
# Batch: BAT-0BF91A
# Witness: bdb1c1b58ad0547a

import os
import pytest

README_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..", "..", "..",
    "README.md"
)

# Resolve to an absolute path for clarity in failure messages
README_PATH = os.path.abspath(README_PATH)

# Override with the canonical absolute path expected by the task spec
README_PATH = (
    "/Users/brandonshuey/data/ByteForge/Repositories/"
    "e0710c02-7a18-467f-8a6e-519bafe16e3e/.bf-worktrees/fb4a5a61/README.md"
)


def test_readme_has_commands():
    """
    REQ-95C535: README must contain verbatim install, run, and test commands.

    Required command references:
      - Install:  pip install  (package installation)
      - Run:      python adventure.py  OR  python -m adventure
      - Test:     pytest  OR  python -m pytest
    """
    assert os.path.exists(README_PATH), (
        f"README.md not found at {README_PATH}. "
        "The file must exist and document install, run, and test commands."
    )

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # --- install command ---
    assert "pip install" in content, (
        "README.md must contain a verbatim 'pip install' command "
        "so users know how to install dependencies."
    )

    # --- run command ---
    has_run_command = (
        "python adventure.py" in content
        or "python -m adventure" in content
    )
    assert has_run_command, (
        "README.md must contain a verbatim run command: "
        "'python adventure.py' or 'python -m adventure'."
    )

    # --- test command ---
    has_test_command = (
        "pytest" in content
        or "python -m pytest" in content
    )
    assert has_test_command, (
        "README.md must contain a verbatim test command: "
        "'pytest' or 'python -m pytest'."
    )
