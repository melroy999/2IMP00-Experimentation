import z3

array_name_dictionary = {}
conversion_cache = {}
s = z3.Solver()


class TransitDict(dict):
    """A dictionary that returns the key upon query if the key is not present within the dictionary"""
    def __missing__(self, key):
        return key


# Convert the used symbols to their Z3 SMT2.0 counterpart.
smt_operator_mappings = TransitDict()
smt_operator_mappings["<>"] = "!="
smt_operator_mappings["!"] = "not"
smt_operator_mappings["&&"] = "and"
smt_operator_mappings["||"] = "or"
smt_operator_mappings["%"] = "mod"


def to_simple_ast(ast):
    """Convert the TextX expression AST to a simpler and more tidy format similar to the SMT2.0 standard"""
    class_name = ast.__class__.__name__
    if class_name in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if ast.right is None:
            return to_simple_ast(ast.left)
        else:
            return smt_operator_mappings[ast.op], to_simple_ast(ast.left), to_simple_ast(ast.right)
    elif class_name == "Primary":
        if ast.value is not None:
            if ast.sign == "-":
                return -1 * ast.value
            elif ast.sign == "not":
                return not ast.value
            else:
                return ast.value
        elif ast.ref is not None:
            if ast.sign == "-":
                return "-", 0, to_simple_ast(ast.ref)
            if ast.sign == "not":
                return "not", to_simple_ast(ast.ref)
            return to_simple_ast(ast.ref)
        else:
            if ast.sign == "-":
                return "-", 0, to_simple_ast(ast.body)
            if ast.sign == "not":
                return "not", to_simple_ast(ast.body)
            else:
                return to_simple_ast(ast.body)
    elif class_name == "ExpressionRef":
        if ast.index is None:
            return "var", ast.ref
        else:
            return "var[]", ast.ref, to_simple_ast(ast.index)
    elif class_name == "VariableRef":
        if ast.index is None:
            return "var", ast.var.name
        else:
            return "var[]", ast.var.name, to_simple_ast(ast.index)
    else:
        raise Exception("No implementation exists for the simple ast conversion of class [%s]" % class_name)


def to_z3_format_rec(ast, variables):
    """Recursively convert the smt tree structure to a smt2.0 string"""
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
    """Convert the smt tree structure to a smt2.0 string, and cache the conversion"""
    if ast in conversion_cache:
        parsed, used_vars = conversion_cache[ast]
    else:
        used_vars = {}
        parsed = to_z3_format_rec(ast, used_vars)
        conversion_cache[ast] = parsed, used_vars

    return parsed, used_vars


def __generate_z3_variable_declarations(used_variables, variables):
    """Generate the smt2.0 variables declaration entries"""
    used_var_types = {
        v: "Bool" if variables[v_base].type.base == "Boolean" else "Int" for v, v_base in used_variables.items()
    }
    return " ".join(["(declare-const %s %s)" % (v, t) for v, t in used_var_types.items()])


def __to_z3_assertion(smt_string, variable_declarations):
    """Create an assertion string for the given variable declarations and smt2.0 string"""
    return "%s (assert %s)" % (variable_declarations, smt_string)


def __to_z3_object(smt_string):
    """Convert the smt2.0 string to a z3 object"""
    return z3.parse_smt2_string(smt_string)


def to_z3_format(ast, variables):
    """Convert the given smt tree structure to a z3 object, given a list of used variables"""
    parsed, used_variables = to_smt_format_string(ast)
    variable_declarations = __generate_z3_variable_declarations(used_variables, variables)
    assertion = __to_z3_assertion(parsed, variable_declarations)
    return __to_z3_object(assertion)


def z3_truth_check(ast, variables, for_all=True):
    """Check whether the given smt tree structure always holds true (default), or has a satisfiable assignment (alt)"""
    parsed, used_variables = to_smt_format_string(ast)
    variable_declarations = __generate_z3_variable_declarations(used_variables, variables)
    result = __z3_check_truth(for_all, parsed, variable_declarations)

    return result


def z3_opr_check(binary_operator, ast1, ast2, variables, for_all=False):
    """Check whether the given smt tree structures have a common solution under the given operator (default) or
    check whether the combination under the operator always holds true (alt)"""
    parsed_1, used_variables_1 = to_smt_format_string(ast1)
    parsed_2, used_variables_2 = to_smt_format_string(ast2)
    variable_declarations = __generate_z3_variable_declarations({**used_variables_1, **used_variables_2}, variables)
    parsed = "(%s %s %s)" % (binary_operator, parsed_1, parsed_2)
    result = __z3_check_truth(for_all, parsed, variable_declarations)

    return result


def __z3_check_truth(for_all, parsed, variable_declarations):
    """Check the truth of the given z3 object. for_all specifies if it must hold for all values,
    or whether just a single satisfiable assignment should exist"""
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
