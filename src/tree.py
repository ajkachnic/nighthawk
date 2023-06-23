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

    def __str__(self) -> str:
        return self.name


@dataclass(init=False)
class FunctionDeclaration(_Ast):
    name: str
    args: List[Name]
    body: List[_Statement] # = field(default_factory=list)

    def __init__(self, *args):
        self.name = args[0]
        self.args = []
        self.body = []

        for arg in args[1:]:
            if isinstance(arg, Name):
                self.args.append(arg)
            elif isinstance(arg, _Statement):
                self.body.append(arg)

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
