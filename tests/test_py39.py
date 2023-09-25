from __future__ import annotations

from tests.utils import TargetTester

tester = TargetTester((3, 9))


def test_typing_extensions_import():
    tester.expect(
        "from typing import Concatenate", "from typing_extensions import Concatenate"
    )


def test_typing_extensions_import_with_typing_import():
    tester.expect(
        "from typing import Concatenate, Callable",
        "from typing_extensions import Concatenate\nfrom typing import Callable",
    )


def test_typing_extensions_import_with_other_import():
    tester.expect(
        "from dataclasses import dataclass\nfrom typing import Concatenate",
        "from dataclasses import dataclass\nfrom typing_extensions import Concatenate",
    )
