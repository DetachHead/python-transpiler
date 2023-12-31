from __future__ import annotations

import sys
from pathlib import Path
from subprocess import CalledProcessError, run
from typing import cast


def test_cli(tmp_path: Path):
    try:
        run(
            [
                Path("./pw.bat" if sys.platform == "win32" else "./pw").resolve(),
                "run",
                "python",
                "-m",
                "python_transpiler.cli",
                tmp_path,
                "--target",
                "3.10",
            ],
            check=True,
            cwd="tests/fixtures/cli",
            capture_output=True,
        )
    except CalledProcessError as e:
        raise Exception(str(cast(str | bytes | None, e.stderr))) from e
    assert (tmp_path / "package/__init__.py").exists()
    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "README.md").exists()
