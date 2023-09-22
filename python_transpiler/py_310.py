from __future__ import annotations

from ast import ImportFrom, alias
from dataclasses import dataclass

from typing_extensions import override

from python_transpiler.utils import BaseVisitor, PythonVersion


@dataclass(frozen=True)
class Import:
    module: str
    name: str


import_replacements = {Import("typing", "Never"): Import("typing_extensions", "Never")}


class Py310Visitor(BaseVisitor):
    @override
    @staticmethod
    def python_version() -> PythonVersion:
        return (3, 10)

    @override
    def visit_ImportFrom(self, node: ImportFrom) -> list[ImportFrom]:
        result = []
        for name in node.names:
            new_import = (
                import_replacements.get(Import(node.module, name.name))
                if node.module
                else None
            )
            if new_import:
                node.names.remove(name)
                result.append(
                    ImportFrom(
                        module=new_import.module,
                        names=[  # type:ignore[no-any-expr]
                            alias(name=new_import.name)
                        ],
                    )
                )
        if node.names:
            result.append(node)
        return result
