from typing import List, Optional
from dataclasses import dataclass, field

from lark import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta


class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


@dataclass
class Name(_Ast):
    name: str


@dataclass
class FunctionDeclaration(_Ast):
    name: str
    args: List[Name]
    body: List[_Statement] = field(default_factory=list)


@dataclass
class ConstantDeclaration(_Ast):
    name: Name
    value: int


@dataclass
class PrintStatement(_Statement):
    string: str


class ToAst(Transformer):
    # Define extra transformation functions, for rules that don't correspond to an AST class.

    def STRING(self, s):
        # Remove quotation marks
        return s[1:-1]

    def DEC_NUMBER(self, n):
        return int(n)

    def NAME(self, n):
        return Name(n.value)

    @v_args(inline=True)
    def start(self, x):
        return x
