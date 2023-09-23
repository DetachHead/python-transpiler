from __future__ import annotations

from pathlib import Path
from subprocess import run

import python_transpiler


def test_single_file(tmp_path: Path):
    run(
        [
            "poetry",
            "run",
            "python",
            Path(python_transpiler.__file__).parent / "cli.py",
            "tests/fixtures/cli/single_file.py",
            "--output-dir",
            tmp_path,
            "--target",
            "3.10",
        ],
        check=True,
    )
    assert (
        tmp_path / "single_file.py"
    ).read_text() == "from __future__ import annotations\nfrom typing_extensions import Never"


def test_multiple_files(tmp_path: Path):
    run(
        [
            "poetry",
            "run",
            "python",
            Path(python_transpiler.__file__).parent / "cli.py",
            "tests/fixtures/cli/multiple_files/",
            "--output-dir",
            tmp_path,
            "--target",
            "3.10",
        ],
        check=True,
    )
    assert len(list((tmp_path).iterdir())) == 3
