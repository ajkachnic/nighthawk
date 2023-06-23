import tree

def evaluate_expression(node: tree.Expression):
    """
    Evaluate an expression, using simple tree walking. Used for constant folding.
    """
    match node:
        case tree.Add(lhs, rhs):
            return evaluate_expression(lhs) + evaluate_expression(rhs)
        case tree.Sub(lhs, rhs):
            return evaluate_expression(lhs) - evaluate_expression(rhs)
        case tree.Mul(lhs, rhs):
            return evaluate_expression(lhs) * evaluate_expression(rhs)
        case tree.Div(lhs, rhs):
            return evaluate_expression(lhs) / evaluate_expression(rhs)
        case tree.And(lhs, rhs):
            return evaluate_expression(lhs) and evaluate_expression(rhs)
        case tree.Or(lhs, rhs):
            return evaluate_expression(lhs) or evaluate_expression(rhs)
        case tree.Equal(lhs, rhs):
            return evaluate_expression(lhs) == evaluate_expression(rhs)
        case tree.NotEqual(lhs, rhs):
            return evaluate_expression(lhs) != evaluate_expression(rhs)
        case tree.LessThan(lhs, rhs):
            return evaluate_expression(lhs) < evaluate_expression(rhs)
        case tree.GreaterThan(lhs, rhs):
            return evaluate_expression(lhs) > evaluate_expression(rhs)
        case tree.LessThanEqual(lhs, rhs):
            return evaluate_expression(lhs) <= evaluate_expression(rhs)
        case tree.GreaterThanEqual(lhs, rhs):
            return evaluate_expression(lhs) >= evaluate_expression(rhs)
        case tree.Neg(expr):
            return -evaluate_expression(expr)
        # case tree.Not(expr):
        #     return not evaluate_expression(expr)
        case tree.Name(name):
            raise RuntimeError(f"Cannot evaluate variable {name} in constant expression")
        case tree.Boolean(value=value):
            return value
        case n if isinstance(n, int):
            return n
        case _:
            raise RuntimeError(f"Cannot evaluate expression {node} in constant expression")
