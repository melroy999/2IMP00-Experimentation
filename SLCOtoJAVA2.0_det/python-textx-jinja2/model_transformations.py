from jinja2_filters import get_instruction
from range_analysis import get_ranges
from smt_functions import z3_truth_check, to_simple_ast

# An expression that represents an object that is always true, used as replacement for empty guards.
from variable_locking import assign_lock_ids_to_class_variables, construct_valid_lock_order, propagate_used_variables, \
    propagate_lock_variables

true_expression = type("Expression", (object,), {
    "left": type("Primary", (object,), {"value": True, "sign": "", "body": None, "ref": None})(),
    "op": "",
    "right": None,
    "smt": True,
    "is_trivially_satisfiable": True,
    "is_trivially_unsatisfiable": False,
    "__repr__": lambda self: get_instruction(self),
})()


def object_to_comment(m):
    """Convert a TextX object to a comment string"""
    model_class = m.__class__.__name__

    if model_class == "Transition":
        return "from %s to %s {%s}" % (m.source, m.target, "; ".join(object_to_comment(v) for v in m.statements))
    elif model_class == "Assignment":
        var_str = m.left.var.name + ("[" + object_to_comment(m.left.index) + "]" if m.left.index is not None else "")
        exp_str = object_to_comment(m.right)
        return "%s = %s" % (var_str, exp_str)
    elif model_class == "Composite":
        statement_strings = [object_to_comment(m.guard)]
        statement_strings += [object_to_comment(s) for s in m.assignments]
        return "[%s]" % "; ".join(statement_strings)
    elif model_class in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if m.op == "":
            return object_to_comment(m.left)
        else:
            return "%s %s %s" % (object_to_comment(m.left), m.op, object_to_comment(m.right))
    elif model_class == "Primary":
        if m.value is not None:
            exp_str = str(m.value).lower()
        elif m.ref is not None:
            exp_str = m.ref.ref + ("[%s]" % object_to_comment(m.ref.index) if m.ref.index is not None else "")
        else:
            exp_str = "(%s)" % object_to_comment(m.body)
        return ("not (%s)" if m.sign == "not" else m.sign + "%s") % exp_str
    elif model_class == "VariableRef":
        return m.var.name + ("[%s]" % object_to_comment(m.index) if m.index is not None else "")
    elif model_class == "ActionRef":
        return m.act.name
    else:
        return "[c]NYI"


#
#
#


def propagate_simplification(model, variables=None):
    """Make simplifications where possible in the model, including the detection of trivially (un)satisfiability"""
    class_name = model.__class__.__name__
    if class_name == "Class":
        for sm in model.statemachines:
            if len(set(model.name_to_variable).intersection(set(sm.name_to_variable))) > 0:
                raise Exception("The class and state machine have variable names in common.")
            variables = {**model.name_to_variable, **sm.name_to_variable}
            for t in sm.transitions:
                propagate_simplification(t, variables)

    elif class_name == "Transition":
        propagate_simplification(model.guard, variables)
        for s in model.statements:
            propagate_simplification(s, variables)

        # Check if the guard is trivially satisfiable.
        model.is_trivially_satisfiable = model.guard.is_trivially_satisfiable
        model.is_trivially_unsatisfiable = model.guard.is_trivially_unsatisfiable

        if model.is_trivially_satisfiable and model.guard.smt is not True:
            model.comment_string += " (trivially satisfiable)"
        if model.is_trivially_unsatisfiable:
            model.comment_string += " (trivially unsatisfiable)"

        # If the guard is a composite, and it is trivially satisfiable, split.
        if model.guard.__class__.__name__ == "Composite" and model.is_trivially_satisfiable:
            model.statements = [model.guard] + model.statements
            model.guard = true_expression

        # Are any of the expressions trivial? Remove the appropriate statements.
        trivially_satisfiable_expression_ids = []
        for i in range(0, len(model.statements)):
            statement = model.statements[i]
            if statement.__class__.__name__ == "Expression":
                if statement.is_trivially_satisfiable:
                    # Append to the start so that we don't delete the wrong items.
                    trivially_satisfiable_expression_ids.insert(0, i)
                elif statement.is_trivially_unsatisfiable:
                    # Forget about everything after the statement--it is unreachable code.
                    model.always_fails = True
                    model.statements = model.statements[:i]
                    break

        # Remove the expressions that are always true.
        for i in trivially_satisfiable_expression_ids:
            model.statements.pop(i)

    elif class_name == "Composite":
        propagate_simplification(model.guard, variables)
        for a in model.assignments:
            propagate_simplification(a, variables)

        # Check if the guard is trivially satisfiable.
        model.is_trivially_satisfiable = model.guard.is_trivially_satisfiable
        model.is_trivially_unsatisfiable = model.guard.is_trivially_unsatisfiable

    elif class_name == "Expression":
        # Use SMT do determine whether the formula is trivially (un)satisfiable.
        model.is_trivially_satisfiable = z3_truth_check(model.smt, variables)
        model.is_trivially_unsatisfiable = not z3_truth_check(model.smt, variables, False)


#
#
#


def transform_statement(s):
    """Transform the statement such that it provides all the data required for the code conversion"""
    class_name = s.__class__.__name__
    if class_name == "Composite":
        # Always make sure that a guard expression exists, defaulting to a "True" expression.
        s.guard = true_expression if s.guard is None else transform_statement(s.guard)
        s.assignments = [transform_statement(a) for a in s.assignments]
    elif class_name == "Expression":
        s.smt = to_simple_ast(s)
        # Provide equality and hash functions such that the expressions can be added to a set.
        type(s).__eq__ = lambda self, other: self.smt == other.smt
        type(s).__hash__ = lambda self: hash(self.__repr__())

    # Give all statements a readable string representation corresponding to the associated java code.
    type(s).__repr__ = lambda self: get_instruction(self)

    return s


def transform_transition(t):
    """Transform the transition such that it provides all the data required for the code conversion"""
    t.source = t.source.name
    t.target = t.target.name
    t.always_fails = False
    t.comment_string = object_to_comment(t)

    # We determine whether a transition is guarded by looking whether the first statement is an expression.
    t.statements = [transform_statement(_s) for _s in t.statements]
    first_statement = t.statements[0]

    # Convert a tau ActionRef to a true statement.
    class_name = first_statement.__class__.__name__
    if class_name == "ActionRef":
        if first_statement.act.name == "tau":
            t.statements[0] = first_statement = true_expression
            class_name = "Expression"

    # Find the guard expression of the transition.
    if class_name in ["Expression", "Composite"]:
        # Cut off the first statement, since it is part of the guard now.
        t.guard = first_statement
        t.statements = t.statements[1:]
    else:
        # No guard is present. Set the true expression as the guard.
        t.guard = true_expression

    # Make a function that easily gets the transition expression.
    t.guard_expression = t.guard.guard if class_name == "Composite" else t.guard

    # Make a human readable format of the transition.
    type(t).__repr__ = lambda self: self.comment_string

    return t


# noinspection SpellCheckingInspection
def transform_state_machine(sm, c):
    """Transform the state machine such that it provides all the data required for the code conversion"""
    sm.initialstate = sm.initialstate.name
    sm.states = [s.name for s in sm.states]
    sm.name_to_variable = {v.name: v for v in sm.variables}
    sm.parent_class = c
    sm.transitions = [transform_transition(t) for t in sm.transitions]
    sm.adjacency_list = {
        s: [
            t for t in sm.transitions if t.source == s
        ] for s in sm.states
    }
    for v in sm.variables:
        type(v).__repr__ = lambda v: "%s (%s)" % (
            v.name, (v.type.base if v.type.size == 0 else "%s[%s]" % (v.type.base, v.type.size))
        )


def transform_model(model):
    """Transform the model such that it provides all the data required for the code conversion"""
    for c in model.classes:
        c.name_to_variable = {v.name: v for v in c.variables}
        for sm in c.statemachines:
            transform_state_machine(sm, c)

        # Give the variables a readable representation.
        for v in c.variables:
            type(v).__repr__ = lambda v: "%s (%s)" % (
                v.name, (v.type.base if v.type.size == 0 else "%s[%s]" % (v.type.base, v.type.size))
            )

    # Check which variables have been used in the model and find all variables that need to be locked.
    for c in model.classes:
        assign_lock_ids_to_class_variables(c)
        propagate_simplification(c)
        propagate_used_variables(c)
        propagate_lock_variables(c, c.name_to_variable.keys())
        construct_valid_lock_order(c)

    # Ensure that each class has references to its objects.
    for c in model.classes:
        c.objects = []
    for _o in model.objects:
        _o.type.objects.append(_o)

    return model
