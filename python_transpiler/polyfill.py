import _collections_abc
from typing import _TupleType, _alias
import typing
import sys

if sys.version_info < (3, 9):
    typing.List._inst = True
    typing.Tuple._inst = True
    typing.Set._inst = True
    typing.FrozenSet._inst = True
    typing.Dict._inst = True
    typing.Type._inst = True

DictKeys = _alias(_collections_abc.dict_keys, 2, name="DictKeys")
DictValues = _alias(_collections_abc.dict_values, 2, name="DictValues")
DictItems = _alias(_collections_abc.dict_items, 2, name="DictItems")
# TODO: find any other fake-generic types
