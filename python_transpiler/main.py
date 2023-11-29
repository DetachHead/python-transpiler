from __future__ import annotations

from typing import TYPE_CHECKING

from python_transpiler.py_38 import Py38Visitor
from python_transpiler.py_39 import Py39Visitor
from python_transpiler.py_310 import Py310Visitor

if TYPE_CHECKING:
    from ast import Module

    from python_transpiler.utils import PythonVersion


def transpile(module: Module, target: PythonVersion) -> set[str]:
    """transpiles the specified module to be compatible with the target python version

    :returns: the pypi names of any additional dependencies that are required for the module to work
    on the target version (eg. polyfills such as `exceptiongroup`)"""
    dependencies = set[str]()
    # versions will probably need to be in highest to lowest order
    for visitor_class in (Py310Visitor, Py39Visitor, Py38Visitor):
        visitor = visitor_class()
        if visitor.python_version() >= target:
            visitor.visit(module)
            dependencies.update(visitor.dependencies)
    return dependencies
