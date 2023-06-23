from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Statement:
    pass

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
    def __repr__(self) -> str:
        return f"Type(variant={self.variant}, arg={self.arg})"
    
    def __str__(self) -> str:
        match self.variant:
            case "word":
                return "w"
            case "long":
                return "l"
            case "single":
                return "s"
            case "double":
                return "d"
            case "byte":
                return "b"
            case "halfword":
                return "h"
            case "aggregate":
                return f":{self.arg.name}"


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
    JNZ = "Jnz"
    JMP = "Jmp"
    CALL = "Call"
    ALLOC4 = "Alloc4"
    ALLOC8 = "Alloc8"
    ALLOC16 = "Alloc16"
    STORE = "Store"
    LOAD = "Load"
    BLIT = "Blit"


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
    
class Copy(Instruction[T]):
    """
    Copies either a temporary or literal value
    """

    def __init__(self, value: Value):
        super().__init__(InstrTag.COPY, value)

    def __str__(self) -> str:
        return f"copy {self.args[0]}"
    
class Ret(Instruction[T]):
    """
    Return from a function, optionally with a value
    """

    def __init__(self, value: Optional[Value] = None):
        super().__init__(InstrTag.RET, value)

    def __str__(self) -> str:
        if self.args[0] is None:
            return "ret"
        return f"ret {self.args[0]}"

class Jnz(Instruction[T]):
    """
    Jumps to first label if a value is nonzero or to the second one otherwise
    """

    def __init__(self, value: Value, nonzero: str, otherwise: str):
        super().__init__(InstrTag.JNZ, value, nonzero, otherwise)

    def __str__(self) -> str:
        return f"jnz {str(self.args[0])}, @{self.args[1]}, @{self.args[2]}"
    
    def __repr__(self) -> str:
        return f"Jnz(value={self.args[0]}, nonzero={self.args[1]}, otherwise={self.args[2]})"

class Jmp(Instruction[T]):
    """
    Unconditionally jumps to a label
    """

    def __init__(self, label: str):
        super().__init__(InstrTag.JMP, label)

    def __str__(self) -> str:
        return f"jmp @{self.args[0]}"
    
class Call(Instruction[T]):
    """
    Calls a function
    """

    def __init__(self, function: str, args: list[(Type, Value)]):
        super().__init__(InstrTag.CALL, function, args)

    def __str__(self) -> str:
        args = ", ".join([f"{ty} {val}" for ty, val in self.args[1]])
        return f"call ${self.args[0]}({args})"
    
    def __repr__(self) -> str:
        return f"Call(function={self.args[0]}, args={self.args[1]})"
    
class Alloc4(Instruction[T]):
    """
    Allocates 4-byte aligned area on the stack
    """
    def __init__(self, size: int):
        super().__init__(InstrTag.ALLOC4, size)

    def __str__(self) -> str:
        return f"alloc4 {self.args[0]}"

class Alloc8(Instruction[T]):
    """
    Allocates 8-byte aligned area on the stack
    """
    def __init__(self, size: int):
        super().__init__(InstrTag.ALLOC8, size)

    def __str__(self) -> str:
        return f"alloc8 {self.args[0]}"

class Alloc16(Instruction[T]):
    """
    Allocates 16-byte aligned area on the stack
    """
    def __init__(self, size: int):
        super().__init__(InstrTag.ALLOC16, size)

    def __str__(self) -> str:
        return f"alloc16 {self.args[0]}"

class Store(Instruction[T]):
    """
    Stores a value into memory pointed to by destination.
    """

    def __init__(self, ty: Type, value: Value, destination: Value):
        super().__init__(InstrTag.STORE, ty, value, destination)

    def __str__(self) -> str:
        return f"store{self.args[0]} {self.args[1]}, {self.args[2]}"
    
class Load(Instruction[T]):
    """
    Loads a value from memory pointed to by source.
    """

    def __init__(self, ty: Type, source: Value):
        super().__init__(InstrTag.LOAD, ty, source)

    def __str__(self) -> str:
        return f"load{self.args[0]} {self.args[1]}"
    
class Blit(Instruction[T]):
    """
    Copy `n` bytes from the source address to the destination address.

    n must be a constant value.
    """

    def __init__(self, source: Value, destination: Value, n: int):
        super().__init__(InstrTag.BLIT, source, destination, n)

    def __str__(self) -> str:
        return f"blit {self.args[0]}, {self.args[1]}, {self.args[2]}"

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
            out = "export "

        if self.section is not None:
            out += f'section "{self.section}"'

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

    def __str__(self) -> str:
        out = f"{str(self.linkage)}function";
        if self.return_type is not None:
            out += f" {self.return_type}"

        out += " ${}({})".format(str(self.name), "\n".join([ f"{ty} {temp}" for (ty, temp) in self.args ]))

        out += " {\n"

        for blk in self.body:
            out += f"{str(blk)}\n"

        out += "}"

        return out

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

    def __str__(self) -> str:
        out = f"{str(self.linkage)}data ${self.name} = "

        if self.align is not None:
            out += f"align {self.align} "

        out += "{"
        out += ", ".join([f"{ty} {item}" for ty, item in self.items])
        out += "}"

        return out

@dataclass
class Module:
    """
    A complete IL file
    """

    functions: list[Function] = field(default_factory=list)
    data: list[DataDef] = field(default_factory=list)
    types: list[TypeDef] = field(default_factory=list)

    def add_function(self, function: Function):
        """
        Adds a function to the module
        """
        self.functions.append(function)

    def add_type(self, ty: TypeDef):
        """
        Adds a type to the module
        """
        self.types.append(ty)

    def add_data(self, data: DataDef):
        """
        Adds a data definition to the module
        """
        self.data.append(data)

    def __str__(self) -> str:
        out = ""
        for f in self.functions:
            out += f"{str(f)}\n"

        for d in self.data:
            out += f"{str(d)}\n"

        for t in self.types:
            out += f"{str(t)}\n"

        return out