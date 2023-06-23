from typing import List, Optional
from dataclasses import dataclass, field

from lark import Lark, Token, ast_utils, Transformer, v_args
from lark.tree import Meta


class _Ast(ast_utils.Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass


class _Statement(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

class Expression(_Ast):
    # This will be skipped by create_transformer(), because it starts with an underscore
    pass

@dataclass(repr=False)
class Name(_Ast):
    name: str

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Name('{self.name}')"

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

@dataclass
class Add(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class Sub(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class Mul(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class Div(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class And(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class Or(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class Equal(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class NotEqual(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class LessThan(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class GreaterThan(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class LessThanEqual(Expression):
    lhs: Expression
    rhs: Expression

@dataclass
class GreaterThanEqual(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class Neg(Expression):
    op: Expression

class Boolean(Expression):
    value: bool

    def __init__(self, value: Token):
        self.value = value.value == 'true'

    def __repr__(self) -> str:
        return f"Boolean({self.value})"