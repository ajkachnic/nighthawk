from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, TypeVar




T = TypeVar("T")


@dataclass
class Statement:
    pass


# class Type(Enum):
#     WORD = "word"
#     LONG = "long"
#     SINGLE = "single"
#     DOUBLE = "double"
#     BYTE = "byte"
#     HALFWORD = "halfword"
#     AGGREGATE = "aggregate"

@dataclass
class TypeDef:
    # Aggregate type name
    name: str

    # Type alignment
    align: Optional[int]

    # Types contained in the aggregate type
    items: list[(Type, int)]

    def __str__(self) -> str:
        out = f"type :{self.name} = "
        if self.align is not None:
            out += f"align {self.align} "

        out += "{"
        out += ", ".join(
            [f"{ty} {count}" if count > 1 else f"{ty}" for ty, count in self.items]
        )
        out += "}"

        return out

class Type(Generic[T]):
    variant: str
    arg: Optional[TypeDef]

    def __init__(self, variant: str, arg: Optional[TypeDef]) -> None:
        self.variant = variant
        self.arg = arg

    def into_abi(self):
        match self.variant:
            case "byte" | "halfword":
                return Word()
            case _:
                return self.variant


# Base Types
Word = Type("word", None)
Long = Type("long", None)
Single = Type("single", None)
Double = Type("double", None)

# Extended Types
Byte = Type("byte", None)
Halfword = Type("halfword", None)

AggregateType = Type("aggregate", TypeDef)


class Value:
    pass


class InstrTag(Enum):
    ADD = "Add"
    SUB = "Sub"
    MUL = "Mul"
    DIV = "Div"
    REM = "Rem"
    CMP = "Cmp"
    AND = "And"
    OR = "Or"
    COPY = "Copy"
    RET = "Ret"


class Instruction(Generic[T]):
    tag: InstrTag
    args: T

    def __init__(self, tag: InstrTag, *args):
        self.tag = tag
        self.args = args


class Add(Instruction[T]):
    """
    Adds values of two temporaries together
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.ADD, value1, value2)

    def __str__(self) -> str:
        return f"add {self.args[0]}, {self.args[1]}"


class Sub(Instruction[T]):
    """
    Subtracts the second value from the first
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.SUB, value1, value2)

    def __str__(self) -> str:
        return f"sub {self.args[0]}, {self.args[1]}"


class Mul(Instruction[T]):
    """
    Multiplies values of two temporaries
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.MUL, value1, value2)

    def __str__(self) -> str:
        return f"mul {self.args[0]}, {self.args[1]}"


class Div(Instruction[T]):
    """
    Divides the first value by the second
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.DIV, value1, value2)

    def __str__(self) -> str:
        return f"div {self.args[0]}, {self.args[1]}"


class Rem(Instruction[T]):
    """
    Returns a remainder from divisionCalculates the remainder of the first value divided by the second
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.REM, value1, value2)

    def __str__(self) -> str:
        return f"rem {self.args[0]}, {self.args[1]}"


class Comparison(Enum):
    SLT = "slt"
    SLE = "sle"
    SEQ = "seq"
    SNE = "sne"
    SGT = "sgt"
    SGE = "sge"


class Cmp(Instruction[T]):
    """
    Performs a comparison of two values
    """

    def __init__(self, ty: Type, comparison: Comparison, value1: Value, value2: Value):
        super().__init__(InstrTag.CMP, ty, comparison, value1, value2)

    def __str__(self) -> str:
        # Can't compare aggregate types
        assert not isinstance(self.args[0], Type.AggregateType)

        return f"c{self.args[1]}{self.args[0]} {self.args[2]} {self.args[3]}"


class And(Instruction[T]):
    """
    Performs a bitwise AND of two values
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.AND, value1, value2)

    def __str__(self) -> str:
        return f"and {self.args[0]}, {self.args[1]}"


class Or(Instruction[T]):
    """
    Performs a bitwise OR of two values
    """

    def __init__(self, value1: Value, value2: Value):
        super().__init__(InstrTag.OR, value1, value2)

    def __str__(self) -> str:
        return f"or {self.args[0]}, {self.args[1]}"


@dataclass
class Temporary(Value):
    value: str

    def __str__(self) -> str:
        return f"%{self.value}"


@dataclass
class Global(Value):
    value: str

    def __str__(self) -> str:
        return f"${self.value}"


@dataclass
class Constant(Value):
    value: int

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Linkage:
    # Specifies whether the target is going to be accessible publicly
    exported: bool

    # Specifies target’s section
    section: Optional[str]

    # Specifies target’s section flags
    flags: Optional[str]

    @staticmethod
    def private():
        return Linkage(exported=False, section=None, flags=None)

    @staticmethod
    def public():
        return Linkage(exported=True, section=None, flags=None)

    def __str__(self) -> str:
        out = ""
        if self.exported:
            out = "export"

        if self.section is not None:
            out += f' section "{self.section}"'

            if self.flags is not None:
                out += f' "{self.flags}"'

            out += " "

        return out





@dataclass
class Block:
    # Label before the block
    label: str

    # List of statements in the block
    statements: list[Statement]

    def add_instruction(self, instruction: Instruction):
        self.statements.append(instruction)

    def __str__(self) -> str:
        out = f"@{self.label}\n"

        # Put each statement on a new line with a tab
        out += "\n".join([f"\t{str(statement)}" for statement in self.statements])

        return out


@dataclass
class Function:
    # Function’s linkage
    linkage: Linkage

    # Function name
    name: str

    # Function arguments
    args: list[(Type, Value)]

    # Return type
    return_type: Optional[Type]

    # Labelled blocks
    body: list[Block] = field(default_factory=list)

    def add_block(self, block: Block):
        """
        Adds a new block to the function
        """
        self.body.append(block)

    def add_instruction(self, instr: Instruction):
        """
        Adds an instruction to the last block
        """
        if self.body.len() > 0:
            self.body[-1].add_instruction(instr)

class DataItem:
    pass

@dataclass
class Symbol(DataItem):
    symbol: str
    offset: Optional[int]

    def __str__(self) -> str:
        if self.offset is None:
            return f"${self.symbol}"
        
        return f"${self.symbol} +{str(self.offset)}"

@dataclass
class String(DataItem):
    string: str

    def __str__(self) -> str:
        return f'"{self.string}"'

@dataclass
class Constant(DataItem):
    value: int

    def __str__(self) -> str:
        return str(self.value)

@dataclass
class DataDef:
    """
    QBE data definition
    """

    linkage: Linkage
    name: str
    align: Optional[int]
    items: list[(Type, DataItem)]