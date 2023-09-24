from __future__ import annotations

from abc import ABC, abstractmethod
from ast import NodeTransformer
from typing import cast


def parse_python_version(values: str) -> PythonVersion:
    return cast(
        PythonVersion,
        # https://github.com/python/mypy/issues/16170
        tuple(int(value) for value in values.split(".")),  # type:ignore[no-any-expr]
    )


PythonVersion = tuple[int, int]


class BaseVisitor(ABC, NodeTransformer):
    @staticmethod
    @abstractmethod
    def python_version() -> PythonVersion: ...
