from __future__ import annotations

from ast import ImportFrom, alias
from dataclasses import dataclass


@dataclass(frozen=True)
class Import:
    module: str
    name: str | None = None
    dependency: str | None = None


@dataclass(frozen=True)
class ReplaceImportsResult:
    imports: list[ImportFrom]
    dependencies: set[str]


def replace_imports(
    imports_to_replace: dict[Import, Import], node: ImportFrom
) -> ReplaceImportsResult:
    result = ReplaceImportsResult(imports=[], dependencies=set())
    for name in node.names:
        new_import = (
            imports_to_replace.get(Import(node.module, name.name))
            or imports_to_replace.get(Import(node.module))
            if node.module
            else None
        )
        if new_import:
            node.names.remove(name)
            result.imports.append(
                ImportFrom(
                    module=new_import.module,
                    names=[  # type:ignore[no-any-expr]
                        alias(name=new_import.name or name.name)
                    ],
                )
            )
            if new_import.dependency:
                result.dependencies.add(new_import.dependency)
    if node.names:
        result.imports.append(node)
    return result
