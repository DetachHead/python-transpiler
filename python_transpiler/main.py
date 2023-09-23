from __future__ import annotations

from typing import TYPE_CHECKING

from python_transpiler.py_310 import Py310Visitor

if TYPE_CHECKING:
    from ast import Module

    from python_transpiler.utils import PythonVersion


def transpile(module: Module, target: PythonVersion):
    # versions will probably need to be in highest to lowest order
    for visitor in (Py310Visitor,):
        if visitor.python_version() >= target:
            visitor().visit(module)
