import z3

array_name_dictionary = {}
conversion_cache = {}


def to_z3_format_rec(ast, _vars):
    # Base types can be returned as-is.
    if type(ast) in (str, int, float, bool):
        return str(ast).lower()

    operator, ops = ast[0], ast[1:]

    # (in)equality operators.
    if operator == "=":
        return "(= %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator in ["!=", "<>"]:
        return "(not (= %s %s))" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == ">":
        return "(> %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "<":
        return "(< %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == ">=":
        return "(>= %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "<=":
        return "(<= %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))

    # Composite operators.
    elif operator == "!":
        return "(not %s)" % to_z3_format_rec(ops[0], _vars)
    elif operator in ["&&", "and"]:
        return "(and %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator in ["||", "or"]:
        return "(or %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "xor":
        return "(xor %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))

    # Math operators.
    elif operator == "+":
        return "(+ %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "-":
        return "(- %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "*":
        return "(* %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "/":
        return "(/ %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "%":
        return "(mod %s %s)" % (to_z3_format_rec(ops[0], _vars), to_z3_format_rec(ops[1], _vars))
    elif operator == "**":
        if type(ops[1]) == int:
            value = (("%s " % to_z3_format_rec(ops[0], _vars)) * ops[1]).strip()
            return "(* %s)" % value
        else:
            raise Exception("Non-constant power operations are not supported", ast)

    # Leaf nodes.
    elif operator == "var":
        _vars[ops[0]] = ops[0]
        return ops[0]
    elif operator == "var[]":
        _var_name = ops[0] + "_"
        if ops[1] not in array_name_dictionary:
            # Create a new name for the index, using a simple counter.
            array_name_dictionary[ops[1]] = "i%s" % len(array_name_dictionary)

        _var_name += array_name_dictionary[ops[1]]
        _vars[_var_name] = ops[0]
        return _var_name
    else:
        raise Exception("Unknown operator in", ast)


def to_smt_format_string(ast):
    if ast in conversion_cache:
        _parsed, _used_vars = conversion_cache[ast]
    else:
        _used_vars = {}
        _parsed = to_z3_format_rec(ast, _used_vars)
        conversion_cache[ast] = _parsed, _used_vars

    return _parsed, _used_vars


def generate_z3_variable_declarations(_used_vars, _vars):
    _used_var_types = {
        _v: "Bool" if _vars[_v_base].type.base == "Boolean" else "Int" for _v, _v_base in _used_vars.items()
    }
    return " ".join(["(declare-const %s %s)" % (_v, _t) for _v, _t in _used_var_types.items()])


def to_z3_assertion(_smt_string, _var_declarations):
    return "%s (assert %s)" % (_var_declarations, _smt_string)


def to_z3_object(_smt_string):
    return z3.parse_smt2_string(_smt_string)


def to_z3_format(ast, _vars):
    _parsed, _used_vars = to_smt_format_string(ast)
    _var_declarations = generate_z3_variable_declarations(_used_vars, _vars)
    _assertion = to_z3_assertion(_parsed, _var_declarations)
    return to_z3_object(_assertion)


def do_z3_and_check(s, ast1, ast2, _vars, _for_all=False):
    _parsed_1, _used_vars_1 = to_smt_format_string(ast1)
    _parsed_2, _used_vars_2 = to_smt_format_string(ast2)
    _var_declarations = generate_z3_variable_declarations({**_used_vars_1, **_used_vars_2}, _vars)
    _parsed = "(and %s %s)" % (_parsed_1, _parsed_2)
    if _for_all:
        _parsed = "(not %s)" % _parsed
    _assertion = to_z3_assertion(_parsed, _var_declarations)

    s.push()
    s.add(z3.parse_smt2_string(_assertion))
    if _for_all:
        result = s.check().r != z3.Z3_L_TRUE
    else:
        result = s.check().r != z3.Z3_L_FALSE
    print(_parsed, result)
    s.pop()
    return result
