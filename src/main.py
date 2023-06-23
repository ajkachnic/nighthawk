from lark import Lark, ast_utils

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
    while True:
        print(parse(input('> ')))
