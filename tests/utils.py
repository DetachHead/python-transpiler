from __future__ import annotations

from ast import parse, unparse
from dataclasses import dataclass
from typing import TYPE_CHECKING

from python_transpiler.main import transpile

if TYPE_CHECKING:
    from python_transpiler.utils import PythonVersion


@dataclass
class TargetTester:
    target: PythonVersion

    def expect(
        self, input_code: str, output: str, dependencies: set[str] | None = None
    ):
        if dependencies is None:
            dependencies = set()
        module = parse(input_code)
        actual_dependencies = transpile(module, self.target)
        assert unparse(module) == output
        assert actual_dependencies == dependencies
