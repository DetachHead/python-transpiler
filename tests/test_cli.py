from __future__ import annotations

from subprocess import run
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_cli(tmp_path: Path):
    run(
        ["poetry", "run", "transpile", tmp_path, "--target", "3.10"],
        check=True,
        cwd="tests/fixtures/cli",
    )
    assert (tmp_path / "package/__init__.py").exists()
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "README.md").exists()
