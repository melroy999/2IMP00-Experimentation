from z3 import *

# Compare the two given abstract syntax trees.
from main import expression_parser


def compare(lhs, rhs):
    return lhs if lhs < rhs else rhs


# A dictionary containing all negations of operators.
operator_negation_dict = {
    # (in)equality operators.
    "==": lambda ops: ("!=", ops[0], ops[1]),
    "!=": lambda ops: ("==", ops[0], ops[1]),
    ">=": lambda ops: ("<", ops[0], ops[1]),
    "<=": lambda ops: (">", ops[0], ops[1]),
    ">": lambda ops: ("<=", ops[0], ops[1]),
    "<": lambda ops: (">=", ops[0], ops[1]),

    # Composite operators.
    "!": lambda ops: ops[0],
    "&&": lambda ops: ("||", negate(ops[0]), negate(ops[1])),
    "||": lambda ops: ("&&", negate(ops[0]), negate(ops[1])),

    # Leaf nodes.
    "var": lambda ops: ("!", ("var", ops[0])),
    "bool": lambda ops: "true" if ops == "false" else "false",
}


def negate(ast):
    operator, operands = ast[0], ast[1:]
    return operator_negation_dict[operator](operands)


print(negate(("!=", ("var", "x"), ("var", "y"))))
print(negate(("&&", ("var", "x"), ("var", "y"))))
print(negate(("&&", ("var", "x"), ("&&", ("var", "y"), ("var", "z")))))
print(negate(("||", ("var", "x"), ("&&", ("var", "y"), ("var", "z")))))
print(negate(("&&", (">=", ("var", "x"), ("int", "0")), (">=", ("var", "y"), ("int", "0")))))
print()


def _to_z3_format_rec(ast, _vars):
    operator, ops = ast[0], ast[1:]

    # (in)equality operators.
    if operator == "==":
        return "(= %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "!=":
        return "(not (= %s %s))" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == ">":
        return "(> %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "<":
        return "(< %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == ">=":
        return "(>= %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "<=":
        return "(<= %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))

    # Composite operators.
    elif operator == "!":
        return "(not %s)" % _to_z3_format_rec(ops[0], _vars)
    elif operator == "&&":
        return "(and %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "||":
        return "(or %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))

    # Math operators.
    elif operator == "+":
        return "(+ %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "-":
        return "(- %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))
    elif operator == "*":
        return "(* %s %s)" % (_to_z3_format_rec(ops[0], _vars), _to_z3_format_rec(ops[1], _vars))

    # Leaf nodes.
    elif operator == "var":
        _vars[ops[0]] = ops[0]
        return ops[0]
    elif operator == "int":
        return ops[0]
    elif operator == "float":
        return ops[0]
    elif operator == "bool":
        return ops[0]


def to_z3_format(ast):
    _variables = {}
    _parsed = _to_z3_format_rec(ast, _variables)
    _smt_program = "%s (assert %s)" % (" ".join(["(declare-const %s Int)" % _v for _v in _variables.keys()]), _parsed)
    return z3.parse_smt2_string(_smt_program)


s = Solver()
parsed = z3.parse_smt2_string('(declare-const x Int) (assert (not (= (> x 0) (>= x 1))))')
s.push()
s.add(parsed)
print(parsed, s.check())

parsed = to_z3_format(expression_parser("(x > 0) == (x >= 1)"))
s.pop()
s.add(parsed)
print(parsed, s.check())

