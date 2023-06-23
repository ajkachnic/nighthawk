from lark import Lark, ast_utils
import sys

import gen
import tree


parser = Lark.open('./src/nighthawk.lark', parser='lalr')

transformer = ast_utils.create_transformer(tree, tree.ToAst())


def parse(text):
    parse_tree = parser.parse(text)
    ast = []

    for decl in parse_tree.children:
        ast.append(transformer.transform(decl))

    return ast


if __name__ == '__main__':
    # Read stdin input from pipe
    text = sys.stdin.read()

    parsed = parse(text)

    generator = gen.CodeGenerator()
    generator.gen(parsed)

    print(str(generator.module))
