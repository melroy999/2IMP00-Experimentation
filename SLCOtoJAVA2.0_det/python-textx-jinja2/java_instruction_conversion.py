class TransitDict(dict):
    """A dictionary that returns the key upon query if the key is not present within the dictionary"""
    def __missing__(self, key):
        return key


# Conversion from SLCO to Java operators.
java_operator_mappings = TransitDict()
java_operator_mappings["<>"] = "!="
java_operator_mappings["="] = "=="
java_operator_mappings["and"] = "&&"
java_operator_mappings["or"] = "||"
java_operator_mappings["not"] = "!"


def get_instruction(m):
    """Get the Java code associated with a given SLCO statement."""
    model_class = m.__class__.__name__

    if model_class == "Assignment":
        var_str = m.left.var.name + ("[" + get_instruction(m.left.index) + "]" if m.left.index is not None else "")
        exp_str = ("(byte) (%s)" if m.left.var.type.base == "Byte" else "%s") % get_instruction(m.right)
        return "%s = %s" % (var_str, exp_str)
    elif model_class == "Composite":
        statement_strings = [get_instruction(m.guard)] if not m.guard.is_trivially_satisfiable else []
        statement_strings += [get_instruction(s) for s in m.assignments]
        return "[%s]" % "; ".join(statement_strings)
    elif model_class in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if m.op == "":
            return get_instruction(m.left)
        elif m.op == "**":
            return "(int) Math.pow(%s, %s)" % (get_instruction(m.left), get_instruction(m.right))
        elif m.op == "%":
            # The % operator in Java is the remainder operator. We want a modulo operation instead.
            return "Math.floorMod(%s, %s)" % (get_instruction(m.left), get_instruction(m.right))
        else:
            return "%s %s %s" % (get_instruction(m.left), java_operator_mappings[m.op], get_instruction(m.right))
    elif model_class == "Primary":
        if m.value is not None:
            exp_str = str(m.value).lower()
        elif m.ref is not None:
            exp_str = m.ref.ref + ("[%s]" % get_instruction(m.ref.index) if m.ref.index is not None else "")
        else:
            exp_str = "(%s)" % get_instruction(m.body)
        return ("!(%s)" if m.sign == "not" else m.sign + "%s") % exp_str
    elif model_class == "VariableRef":
        return m.var.name + ("[%s]" % get_instruction(m.index) if m.index is not None else "")
    else:
        return "// NYI [%s]" % model_class