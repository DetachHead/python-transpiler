import ast

from mypy.checker import TypeTransformVisitor
from mypy.nodes import (
    IndexExpr,
    CallExpr,
    NodeVisitor,
    ImportFrom,
    AssignmentStmt,
    NameExpr,
    OpExpr,
    Node,
    MypyFile,
    ClassDef,
    EllipsisExpr,
    ExpressionStmt,
    Expression,
    TypeAliasExpr,
    TypeAlias,
    FuncDef,
    MemberExpr,
    Block,
    IntExpr,
    StrExpr,
)
from mypy.type_visitor import SyntheticTypeVisitor
from mypy.types import Instance, UnboundType
from mypy.typetraverser import TypeTraverserVisitor
from mypy.visitor import T
from typing_extensions import override


class MypyToAst(NodeVisitor[ast.AST]):
    """converts mypy nodes to ast nodes"""

    def accept_list(self, l: list[Node]) -> list[ast.AST]:
        return [node.accept(self) for node in l]

    @override
    def visit_mypy_file(self, o: MypyFile) -> ast.Module:
        return ast.Module(self.accept_list(o.defs), [])

    @override
    def visit_expression_stmt(self, o: ExpressionStmt) -> ast.Expr:
        return ast.Expr(o.expr.accept(self))

    @override
    def visit_import_from(self, o: ImportFrom) -> ast.ImportFrom:
        return ast.ImportFrom(
            o.id, [ast.alias(name, asname) for name, asname in o.names]
        )

    @override
    def visit_class_def(self, o: ClassDef) -> ast.ClassDef:
        return ast.ClassDef(
            o.name,
            self.accept_list(o.base_type_exprs + o.removed_base_type_exprs),
            [],  # TODO
            self.accept_list(o.defs.body),
            self.accept_list(o.decorators),
            [],  # TODO - type params
        )

    @override
    def visit_func_def(self, o: FuncDef) -> ast.FunctionDef:
        return ast.FunctionDef(
            o.name,
            ast.arguments(
                [],  # TODO
                [
                    ast.arg(
                        arg.variable.name, arg.type_annotation.accept(TypeUnparser())
                    )
                    for arg in o.arguments
                ],
                [],
                [],
                [],
                None,
                [],
            ),
            self.accept_list(o.body.body),
            [],  # TODO
            None,  # TODO: o.docstring
            o.type.ret_type,
            [],
            lineno=o.line,
        )

    @override
    def visit_assignment_stmt(self, o: AssignmentStmt) -> ast.Assign | ast.AnnAssign:
        if o.unanalyzed_type:
            return ast.AnnAssign(
                self.accept_list(o.lvalues),
                o.unanalyzed_type.accept(TypeUnparser()),
                o.rvalue.accept(self),
                0,
            )
        return ast.Assign(
            self.accept_list(o.lvalues), o.rvalue.accept(self), lineno=o.line
        )

    @override
    def visit_name_expr(self, o: NameExpr) -> ast.Name:
        return ast.Name(o.name)

    @override
    def visit_op_expr(self, o: OpExpr) -> ast.BinOp:
        if o.op == "|":
            op = ast.BitOr()
        else:
            raise NotImplementedError
        return ast.BinOp(o.left.accept(self), op, o.right.accept(self))

    @override
    def visit_call_expr(self, o: CallExpr) -> ast.Call:
        return ast.Call(
            o.callee.accept(self), self.accept_list(o.args), []
        )  # TODO keywords

    @override
    def visit_index_expr(self, o: IndexExpr) -> ast.Subscript:
        return ast.Subscript(o.base.accept(self), o.index.accept(self))

    @override
    def visit_ellipsis(self, o: EllipsisExpr) -> ast.Constant:
        return ast.Constant(...)

    @override
    def visit_member_expr(self, o: MemberExpr) -> ast.Attribute:
        return ast.Attribute(o.expr.accept(self), o.name)

    @override
    def visit_int_expr(self, o: IntExpr):
        return ast.Constant(o.value)

    @override
    def visit_str_expr(self, o: StrExpr):
        return ast.Constant(o.value)


class TypeUnparser(SyntheticTypeVisitor):
    def accept_list(self, l):
        return [node.accept(self) for node in l]

    def visit_instance(self, t: Instance) -> ast.AST:
        if t.args:
            return ast.Subscript(ast.Name(t.type.name), self.accept_list(t.args))
        return ast.Name(t.type.name)

    def visit_unbound_type(self, t: UnboundType) -> ast.AST:
        if t.args:
            return ast.Subscript(ast.Name(t.name), self.accept_list(t.args))
        return ast.Name(t.name)
