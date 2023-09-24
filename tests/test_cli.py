from __future__ import annotations

from subprocess import run
from tomllib import loads
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
    assert (
        loads((tmp_path / "pyproject.toml").read_text())[  # type:ignore[no-any-expr]
            "tool"
        ]["poetry"]["dependencies"]["tomli"]
        == "*"
    )
    assert (tmp_path / "README.md").exists()
