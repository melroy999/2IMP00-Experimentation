import z3

array_name_dictionary = {}
conversion_cache = {}
s = z3.Solver()


def to_z3_format_rec(ast, variables):
    # Base types can be returned as-is.
    if type(ast) in (str, int, float, bool):
        return str(ast).lower()

    operator, ops = ast[0], ast[1:]

    # Power operator.
    if operator == "**":
        if type(ops[1]) == int:
            value = (("%s " % to_z3_format_rec(ops[0], variables)) * ops[1]).strip()
            return "(* %s)" % value
        else:
            raise Exception("Non-constant power operations are not supported", ast)

    # Leaf nodes.
    elif operator == "var":
        variables[ops[0]] = ops[0]
        return ops[0]
    elif operator == "var[]":
        variable_name = ops[0] + "_"
        if ops[1] not in array_name_dictionary:
            # Create a new name for the index, using a simple counter.
            array_name_dictionary[ops[1]] = "i%s" % len(array_name_dictionary)

        variable_name += array_name_dictionary[ops[1]]
        variables[variable_name] = ops[0]
        return variable_name

    # Binary operations.
    elif len(ops) == 2:
        return "(%s %s %s)" % (operator, to_z3_format_rec(ops[0], variables), to_z3_format_rec(ops[1], variables))

    # Unary operators.
    elif len(ops) == 1:
        return "(%s %s)" % (operator, to_z3_format_rec(ops[0], variables))

    # Fallback for remaining cases.
    else:
        raise Exception("Unknown operator in", ast)


def to_smt_format_string(ast):
    if ast in conversion_cache:
        parsed, used_vars = conversion_cache[ast]
    else:
        used_vars = {}
        parsed = to_z3_format_rec(ast, used_vars)
        conversion_cache[ast] = parsed, used_vars

    return parsed, used_vars


def __generate_z3_variable_declarations(used_variables, variables):
    used_var_types = {
        v: "Bool" if variables[v_base].type.base == "Boolean" else "Int" for v, v_base in used_variables.items()
    }
    return " ".join(["(declare-const %s %s)" % (v, t) for v, t in used_var_types.items()])


def __to_z3_assertion(smt_string, variable_declarations):
    return "%s (assert %s)" % (variable_declarations, smt_string)


def __to_z3_object(smt_string):
    return z3.parse_smt2_string(smt_string)


def to_z3_format(ast, variables):
    parsed, used_variables = to_smt_format_string(ast)
    variable_declarations = __generate_z3_variable_declarations(used_variables, variables)
    assertion = __to_z3_assertion(parsed, variable_declarations)
    return __to_z3_object(assertion)


def z3_truth_check(ast, variables, for_all=True):
    parsed, used_variables = to_smt_format_string(ast)
    variable_declarations = __generate_z3_variable_declarations(used_variables, variables)
    result = __z3_check_truth(for_all, parsed, variable_declarations)

    return result


def z3_opr_check(binary_operator, ast1, ast2, variables, for_all=False):
    parsed_1, used_variables_1 = to_smt_format_string(ast1)
    parsed_2, used_variables_2 = to_smt_format_string(ast2)
    variable_declarations = __generate_z3_variable_declarations({**used_variables_1, **used_variables_2}, variables)
    parsed = "(%s %s %s)" % (binary_operator, parsed_1, parsed_2)
    result = __z3_check_truth(for_all, parsed, variable_declarations)

    return result


def __z3_check_truth(for_all, parsed, variable_declarations):
    if for_all:
        parsed = "(not %s)" % parsed
    _assertion = __to_z3_assertion(parsed, variable_declarations)
    s.push()
    s.add(z3.parse_smt2_string(_assertion))
    if for_all:
        result = s.check().r != z3.Z3_L_TRUE
    else:
        result = s.check().r != z3.Z3_L_FALSE
    s.pop()
    return result
