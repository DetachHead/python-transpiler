from __future__ import annotations

import pytest

from tests.utils import TargetTester

tester = TargetTester((3, 8))


def test_generic_list():
    tester.expect("list[int]", "list")


def test_generic_annotation():
    tester.expect("a: list[int]", "from typing import List\na: List[int]")


def test_mixed_alias():
    tester.expect(
        """
        from basedtyping import T, Generic
        class A(Generic[T]): ...
        AA = list[T] | A[T]
        """,
        """
        from basedtyping import T, Generic
        from typing import List
        class A(Generic[T]): ...
        A = List[T] | A[T]
        """,
    )
