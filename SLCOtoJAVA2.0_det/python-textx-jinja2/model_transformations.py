from jinja2_filters import get_instruction
from smt_helper_functions import do_z3_truth_check


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
    "smt": True,
    "is_trivially_satisfiable": True,
    "is_trivially_unsatisfiable": False,
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


def gather_used_variables(_s):
    """Gather the variables that are used within the statements"""
    class_name = _s.__class__.__name__
    if class_name in ["Assignment", "Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if _s.right is None:
            return gather_used_variables(_s.left)
        else:
            return gather_used_variables(_s.left).union(gather_used_variables(_s.right))
    elif class_name == "ExpressionRef":
        if _s.index is None:
            return {(_s.ref, None)}
        else:
            return {(_s.ref, get_instruction(_s.index))}
    elif class_name == "VariableRef":
        if _s.index is None:
            return {(_s.var.name, None)}
        else:
            # The index might also hide a variable within it. Account for these as well.
            return {(_s.var.name, get_instruction(_s.index))} | gather_used_variables(_s.index)
    elif class_name == "Primary" and _s.ref is not None:
        return gather_used_variables(_s.ref)
    return set([])


def propagate_locking_variables(_s, _class_variables):
    """For each Composite/Assignment/Expression, add the variables that have to be locked as a field"""
    class_name = _s.__class__.__name__
    if class_name == "Transition":
        propagate_locking_variables(_s.guard, _class_variables)
        for _s2 in _s.statements:
            propagate_locking_variables(_s2, _class_variables)
    elif class_name == "Expression":
        # If the expression is trivially satisfiable, no locks have to be created.
        if _s.is_trivially_satisfiable:
            _s.lock_variables = set([])
        else:
            _s.lock_variables = {_v for _v in _s.used_variables if _v[0] in _class_variables}
    elif class_name == "Assignment":
        _s.lock_variables = {_v for _v in _s.used_variables if _v[0] in _class_variables}
    elif class_name == "Composite":
        _s.lock_variables = set([])
        # If the expression is trivially satisfiable, no locks have to be created for the guard.
        if not _s.guard.is_trivially_satisfiable:
            _s.lock_variables |= {_v for _v in _s.guard.used_variables if _v[0] in _class_variables}
        for _a in _s.assignments:
            _s.lock_variables |= {_v for _v in _a.used_variables if _v[0] in _class_variables}


def transform_statement(_s, _vars):
    """Transform the statement such that it provides all the data required for the code conversion"""
    class_name = _s.__class__.__name__
    if class_name == "Composite":
        _s.guard = transform_statement(_s.guard, _vars)
        _s.assignments = [transform_statement(_a, _vars) for _a in _s.assignments]
        _s.used_variables = gather_used_variables(_s.guard)
        for _a in _s.assignments:
            _s.used_variables |= _a.used_variables
    elif class_name == "Expression":
        # Check if the expression is trivially satisfiable before assigning the smt string.
        _s.smt = to_simple_ast(_s)
        _s.is_trivially_satisfiable = do_z3_truth_check(_s.smt, _vars)
        _s.is_trivially_unsatisfiable = not do_z3_truth_check(_s.smt, _vars, False)
        _s.used_variables = gather_used_variables(_s)
        type(_s).__repr__ = lambda self: "%s" % (expression_to_string(self.smt))
        type(_s).__eq__ = lambda self, other: self.smt == other.smt
        type(_s).__hash__ = lambda self: hash(self.smt.__repr__())
    elif class_name == "Assignment":
        _s.used_variables = gather_used_variables(_s)

    return _s


def transform_transition(_t, _vars):
    """Transform the transition such that it provides all the data required for the code conversion"""
    # We determine whether a transition is guarded by looking whether the first statement is an expression.
    first_statement = _t.statements[0]
    class_name = first_statement.__class__.__name__

    transition_guard = None
    if class_name == "Composite":
        transition_guard = transform_statement(first_statement.guard, _vars)
    elif class_name == "Expression":
        transition_guard = transform_statement(first_statement, _vars)

    if transition_guard is not None and class_name == "Expression":
        _t.statements = _t.statements[1:]

    _t.source = _t.source.name
    _t.target = _t.target.name
    _t.priority = _t.priority
    _t.guard = true_expression if transition_guard is None else transition_guard
    _t.statements = [transform_statement(_s, _vars) for _s in _t.statements]
    _t.is_trivially_satisfiable = _t.guard.is_trivially_satisfiable
    _t.is_trivially_unsatisfiable = _t.guard.is_trivially_unsatisfiable

    _t.used_variables = set([])
    for _s in _t.statements:
        _t.used_variables |= _s.used_variables

    type(_t).__repr__ = lambda self: "%s->%s[%s]" % (
        self.source, self.target, expression_to_string(self.guard.smt)
    )
    return _t


# noinspection SpellCheckingInspection
def transform_state_machine(_sm, _c):
    """Transform the state machine such that it provides all the data required for the code conversion"""
    _sm.initialstate = _sm.initialstate.name
    _sm.states = [_s.name for _s in _sm.states]
    _sm.name_to_variable = {_v.name: _v for _v in _sm.variables}
    _sm.parent_class = _c

    _vars = {**_c.name_to_variable, **_sm.name_to_variable}
    _sm.transitions.sort(key=lambda x: (x.source.name, x.target.name))
    for _t in _sm.transitions:
        transform_transition(_t, _vars)

    _sm.adjacency_list = {
        _s: [
            _t for _t in _sm.transitions if _t.source == _s
        ] for _s in _sm.states
    }

    _sm.used_variables_per_state = {_s: set([]) for _s in _sm.states}
    _sm.used_variables = set([])
    for _s, transitions in _sm.adjacency_list.items():
        for _t in transitions:
            _sm.used_variables_per_state[_s] |= _t.used_variables
            _sm.used_variables |= _t.used_variables
            propagate_locking_variables(_t, _c.name_to_variable.keys())


def transform_model(_ast):
    """Transform the model such that it provides all the data required for the code conversion"""
    for _c in _ast.classes:
        _c.objects = []
        _c.name_to_variable = {_v.name: _v for _v in _c.variables}

        _c.used_variables = set([])
        for _sm in _c.statemachines:
            transform_state_machine(_sm, _c)
            _c.used_variables |= _sm.used_variables

        # Assign unique ids to every variable for locking purposes.
        count = 0
        for key in sorted(_c.name_to_variable.keys()):
            variable = _c.name_to_variable[key]
            variable.lock_id = count
            if variable.type.size > 1:
                count += variable.type.size
            else:
                count += 1
        _c.number_of_class_variables = count

    # Ensure that each class has references to its objects.
    for _o in _ast.objects:
        _o.type.objects.append(_o)

    return _ast
