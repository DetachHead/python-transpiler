# noqa: I002
# typer needs to evaluate the type annotations so can't use __future__.annotations here

import sys
from ast import parse, unparse
from pathlib import Path
from typing import Annotated, Optional

from typer import Option, run

from python_transpiler.main import transpile
from python_transpiler.utils import parse_python_version


def main(
    input_path: Path,
    output_dir: Annotated[Path, Option()],
    # typer doesn't support unions
    target: Optional[str] = None,  # noqa: UP007
):
    input_path = input_path.resolve()
    if input_path.is_dir():
        input_files = list(input_path.rglob("*"))
        parent = input_path
    else:
        input_files = [input_path]
        parent = input_path.parent
    for input_file in input_files:
        module = parse(input_file.read_text(), input_file)
        transpile(
            module,
            (
                parse_python_version(target)
                if target
                else (sys.version_info[0], sys.version_info[1])
            ),
        )
        output_file = output_dir / input_file.relative_to(parent)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(unparse(module))


run(main)
