from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

from mypy.build import BuildManager, BuildSource, build as mypy_build
from mypy.nodes import (
    AssignmentStmt,
    ClassDef,
    Expression,
    FuncDef,
    ImportFrom,
    IndexExpr,
    MypyFile,
    NameExpr,
    OpExpr,
    TypeAliasExpr,
    get_nongen_builtins,
)
from mypy.options import Options
from mypy.treetransform import TransformVisitor
from mypy.typeanal import TypeAnalyser
from mypy.types import Instance, Type, UnboundType
from mypy.typetraverser import TypeTraverserVisitor
from typing_extensions import override

from python_transpiler.utils import PythonVersion
from mypy.nodes import Var

from python_transpiler.visitor import MypyToAst

nongen_builtins = get_nongen_builtins((3, 8))
nongen_builtins_polyfill = {
    "_collections_abc.dict_keys": "polyfill.DictKeys",
    "_collections_abc.dict_values": "polyfill.DictValues",
    "_collections_abc.dict_items": "polyfill.DictItems",
}


class Py38Visitor(TransformVisitor):
    """type hinting generics in standard collections"""

    in_alias = False
    in_class_bases = False

    def __init__(self):
        super().__init__()
        self.test_only = True

    @staticmethod
    def python_version() -> PythonVersion:
        return 3, 8

    # @override # TODO actual base class lol!
    def visit_module(self, node: ast.Module) -> ast.Module:
        o = Options()
        o.preserve_asts = True
        o.incremental = False
        # TODO: use a lower level mypy api to avoid real files
        Path("temp.py").write_text(ast.unparse(node))
        manager = mypy_build(
            sources=[BuildSource("temp.py", "temp")], options=o
        ).manager
        self.manager = manager
        self.manager.semantic_analyzer.options = manager.options
        self.dependencies = set[str]()
        self.imports = defaultdict[str, list[tuple[str, str | None]]](list)
        s = self.manager.semantic_analyzer
        self.type_replacer = PEP585TypeReplacer(
            s, s.tvar_scope, s.plugin, s.options, s.is_typeshed_stub_file
        )
        result = self.visit_mypy_file(manager.tree["temp.py"])
        return result.visit(MypyToAst(result))

    @override
    def visit_mypy_file(self, node: MypyFile) -> MypyFile:
        result = super().visit_mypy_file(node)
        for base, names in self.imports.items():
            result.defs.insert(0, ImportFrom(base, 0, names))
        return result

    @override
    def visit_var(self, node: Var) -> Var:
        if node.fullname == "builtins.list":
            return Var("List", idk_what_goes_here)
        return super().visit_var(node)

    @override
    def visit_type_alias_expr(self, o: TypeAliasExpr) -> TypeAliasExpr:
        in_alias = self.in_alias
        self.in_alias = True
        try:
            return super().visit_type_alias_expr(o)
        finally:
            self.in_alias = in_alias

    @override
    def visit_class_def(self, node: ClassDef) -> ClassDef:
        in_class_bases = self.in_class_bases
        self.in_class_bases = True
        try:
            bases = self.expressions(node.base_type_exprs)
        finally:
            self.in_class_bases = in_class_bases
        new = ClassDef(
            node.name,
            self.block(node.defs),
            node.type_vars,
            bases,
            self.optional_expr(node.metaclass),
        )
        new.fullname = node.fullname
        new.info = node.info
        new.decorators = [self.expr(decorator) for decorator in node.decorators]
        return new

    @override
    def visit_op_expr(self, node: OpExpr) -> OpExpr:
        in_alias = self.in_alias
        if isinstance(node.analyzed, TypeAliasExpr):
            self.in_alias = True
        try:
            return super().visit_op_expr(node)
        finally:
            self.in_alias = in_alias

    @override
    def visit_index_expr(self, o: IndexExpr) -> Expression:
        """Based on SemanticAnalyzer.analyze_type_application"""
        if isinstance(o.base, NameExpr):
            name = nongen_builtins.get(o.base.fullname)
            if name:
                if not (self.in_alias or self.in_class_bases):
                    return o.base
                base, name = name.split(".")
                self.imports[base].append((name, None))
                o.base = NameExpr(name)
                return o
        return o

    @override
    def visit_assignment_stmt(self, node: AssignmentStmt) -> AssignmentStmt:
        if node.unanalyzed_type:
            node.unanalyzed_type.accept(self.type_replacer)
        return super().visit_assignment_stmt(node)

    @override
    def visit_func_def(self, node: FuncDef) -> FuncDef:
        [arg.type_annotation.accept(self.type_replacer) for arg in node.arguments]
        return super().visit_func_def(node)


class PEP585TypeReplacer(TypeAnalyser):
    def visit_unbound_type(
        self, t: UnboundType, defining_literal: bool = False
    ) -> Type:
        # TODO: add imports
        sym = self.api.lookup_qualified(t.name, t)
        if sym:
            node = sym.node
            fullname = node.fullname
            if fullname in nongen_builtins and t.args:
                t.name = nongen_builtins[fullname].split(".")[-1]
        return super().visit_unbound_type(t, defining_literal)
