# noqa: I002
# typer needs to evaluate the type annotations son can't use __future__.annotations here

import sys
from ast import Module, parse, unparse
from pathlib import Path
from typing import Optional

import typer

from python_transpiler.py_310 import Py310Visitor
from python_transpiler.utils import PythonVersion, parse_python_version


def transpile(module: Module, target: PythonVersion):
    # versions will probably need to be in highest to lowest order
    for visitor in (Py310Visitor,):
        if visitor.python_version() >= target:
            visitor().visit(module)


def main(
    input_file: Path, output_file: Path, target: Optional[str] = None  # noqa: UP007
):
    module = parse(input_file.read_text(), input_file)
    transpile(
        module,
        (
            parse_python_version(target)
            if target
            else (sys.version_info[0], sys.version_info[1])
        ),
    )
    output_file.write_text(unparse(module))


if __name__ == "__main__":
    typer.run(main)
