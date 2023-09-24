from __future__ import annotations

from pathlib import Path
from subprocess import run

import python_transpiler


def test_cli(tmp_path: Path):
    run(
        [
            "poetry",
            "run",
            "python",
            Path(python_transpiler.__file__).parent / "cli.py",
            tmp_path,
            "--target",
            "3.10",
        ],
        check=True,
        cwd="tests/fixtures/cli",
    )
    assert (tmp_path / "package/__init__.py").exists()
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "README.md").exists()
