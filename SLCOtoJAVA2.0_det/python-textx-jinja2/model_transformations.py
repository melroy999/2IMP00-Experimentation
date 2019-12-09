class TransitDict(dict):
    """A dictionary that returns the key upon query if the key is not present within the dictionary"""
    def __missing__(self, key):
        return key


smt_operator_mappings = TransitDict()
smt_operator_mappings["<>"] = "!="
smt_operator_mappings["!"] = "not"
smt_operator_mappings["&&"] = "and"
smt_operator_mappings["||"] = "or"
smt_operator_mappings["%"] = "mod"


true_expression = type("Expression", (object,), {
    "left": type("Primary", (object,), {"value": True, "sign": "", "body": None, "ref": None})(),
    "op": "",
    "right": None,
    "smt": True
})()


def expression_to_string(ast):
    """Convert the given SMT ast to a string representation"""
    if type(ast) in [str, int, float, bool]:
        return ast
    else:
        operator, ops = ast[0], ast[1:]

        if len(ops) == 2:
            if operator == "var[]":
                return "%s[%s]" % (expression_to_string(ops[0]), expression_to_string(ops[1]))
            else:
                return "(%s %s %s)" % (expression_to_string(ops[0]), operator, expression_to_string(ops[1]))
        else:
            if operator == "var":
                return "%s" % (expression_to_string(ops[0]))
            else:
                return "(%s %s)" % (operator, expression_to_string(ops[0]))


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
        raise Exception("NYI")


def transform_statement(_s):
    """Transform the statement such that it provides all the data required for the code conversion"""
    class_name = _s.__class__.__name__

    if class_name == "Composite":
        _s.guard = transform_statement(_s.guard)
        _s.assignments = [transform_statement(_a) for _a in _s.assignments]
    elif class_name == "Expression":
        _s.smt = to_simple_ast(_s)
        return _s

    return _s


def transform_transition(_t):
    """Transform the transition such that it provides all the data required for the code conversion"""
    # We determine whether a transition is guarded by looking whether the first statement is an expression.
    first_statement = _t.statements[0]
    class_name = first_statement.__class__.__name__

    transition_guard = None
    if class_name == "Composite":
        transition_guard = transform_statement(first_statement.guard)
    elif class_name == "Expression":
        transition_guard = transform_statement(first_statement)

    _t.source = _t.source.name
    _t.target = _t.target.name
    _t.priority = _t.priority
    _t.guard = true_expression if transition_guard is None else transition_guard
    _t.statements = [transform_statement(_s) for _s in _t.statements]

    if transition_guard is not None and class_name == "Expression":
        _t.statements = _t.statements[1:]

    type(_t).__repr__ = lambda self: "%s->%s[%s]" % (
        self.source, self.target, expression_to_string(self.guard.smt)
    )
    return _t


# noinspection SpellCheckingInspection
def transform_state_machine(_sm):
    """Transform the state machine such that it provides all the data required for the code conversion"""
    _sm.initialstate = _sm.initialstate.name
    _sm.states = [_s.name for _s in _sm.states]
    _sm.name_to_variable = {_v.name: _v for _v in _sm.variables}
    _sm.transitions.sort(key=lambda x: (x.source.name, x.target.name))
    for _t in _sm.transitions:
        transform_transition(_t)

    _sm.adjacency_list = {
        _s: [
            _t for _t in _sm.transitions if _t.source == _s
        ] for _s in _sm.states
    }


def transform_model(_ast):
    """Transform the model such that it provides all the data required for the code conversion"""
    for _c in _ast.classes:
        _c.objects = []
        _c.name_to_variable = {_v.name: _v for _v in _c.variables}

        for _sm in _c.statemachines:
            transform_state_machine(_sm)

        # Assign unique ids to every variable for locking purposes.
        count = 0
        for key in sorted(_c.name_to_variable.keys()):
            variable = _c.name_to_variable[key]
            variable.lock_id = count
            if variable.type.size > 1:
                count += variable.type.size
            else:
                count += 1

    # Ensure that each class has references to its objects.
    for _o in _ast.objects:
        _o.type.objects.append(_o)

    return _ast
