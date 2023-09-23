from __future__ import annotations

from tests.utils import TargetTester

tester = TargetTester((3, 10))


def test_typing_extensions_import():
    tester.expect("from typing import Never", "from typing_extensions import Never")


def test_typing_extensions_import_with_typing_import():
    tester.expect(
        "from typing import Never, Callable",
        "from typing_extensions import Never\nfrom typing import Callable",
    )


def test_typing_extensions_import_with_other_import():
    tester.expect(
        "from dataclasses import dataclass\nfrom typing import Never",
        "from dataclasses import dataclass\nfrom typing_extensions import Never",
    )
