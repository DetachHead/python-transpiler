from __future__ import annotations

from ast import parse, unparse
from dataclasses import dataclass
from typing import TYPE_CHECKING

from python_transpiler import transpile

if TYPE_CHECKING:
    from python_transpiler.utils import PythonVersion


@dataclass
class Tester:
    target: PythonVersion

    def expect(self, input_code: str, output: str):
        module = parse(input_code)
        transpile(module, self.target)
        assert unparse(module) == output
