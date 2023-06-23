import eval
import tree
import qbe

class CodeGenerator:
    module: qbe.Module

    def __init__(self):
        self.module = qbe.Module()

    def gen(self, ast: list[tree.ConstantDeclaration | tree.FunctionDeclaration]):
      for decl in ast:
        if isinstance(decl, tree.ConstantDeclaration):
            self.module.add_data(self.gen_const(decl))
        elif isinstance(decl, tree.FunctionDeclaration):
            self.module.add_function(self.gen_func(decl))
        else:
          raise Exception(f'Unknown declaration type: {decl}')

    def gen_const(self, decl: tree.ConstantDeclaration):
        value = eval.evaluate_expression(decl.value)
        ty = qbe.Long

        if isinstance(value, bool):
            value = int(value)
            ty = qbe.Byte

        if isinstance(value, float):
            ty = qbe.Double

        return qbe.DataDef(
            linkage=qbe.Linkage.private(),
            name=decl.name.name,
            align=None,
            items=[(ty, qbe.Constant(value))]
        )

    def emit_string_literal(self, string: str):
        name = f'str.{len(self.module.data)}'
        data = qbe.DataDef(
            linkage=qbe.Linkage.private(),
            name=name,
            align=None,
            items=[(qbe.Byte, qbe.String(string)), ( qbe.Byte, qbe.Constant(0) )]
        )

        self.module.add_data(data)

        return name

    def gen_func(self, decl: tree.FunctionDeclaration):
        block = qbe.Block(label='entry', statements=[])
        for stmt in decl.body:
            if isinstance(stmt, tree.PrintStatement):
              literal = self.emit_string_literal(stmt.string)

              block.add_instruction(qbe.Call(
                  function="printf",
                  args=[(qbe.Long, qbe.Global(literal) )]
              ))
          
        block.add_instruction(qbe.Ret())
                
        return qbe.Function(
            linkage=qbe.Linkage.public(),
            name=str(decl.name),
            args=[],
            return_type=None,
            body=[block]
        )