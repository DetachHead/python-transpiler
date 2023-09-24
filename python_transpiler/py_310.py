from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from python_transpiler.import_replacer import Import, replace_imports
from python_transpiler.utils import BaseVisitor, PythonVersion

if TYPE_CHECKING:
    from ast import ImportFrom


class Py310Visitor(BaseVisitor):
    @override
    @staticmethod
    def python_version() -> PythonVersion:
        return (3, 10)

    @override
    def visit_ImportFrom(self, node: ImportFrom) -> list[ImportFrom]:
        result = replace_imports(
            {
                Import("typing", "Never"): Import("typing_extensions", "Never"),
                Import("tomllib"): Import("tomli", dependency="tomli"),
            },
            node,
        )
        self.dependencies.update(result.dependencies)
        return result.imports
