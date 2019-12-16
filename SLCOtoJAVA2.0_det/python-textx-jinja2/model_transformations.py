from jinja2_filters import get_instruction
from range_analysis import get_ranges
from smt_functions import z3_truth_check, to_simple_ast

# An expression that represents an object that is always true, used as replacement for empty guards.
true_expression = type("Expression", (object,), {
    "left": type("Primary", (object,), {"value": True, "sign": "", "body": None, "ref": None})(),
    "op": "",
    "right": None,
    "smt": True,
    "is_trivially_satisfiable": True,
    "is_trivially_unsatisfiable": False,
    "__repr__": lambda self: get_instruction(self),
})()


def calculate_lock_ids(c):
    """Assign unique ids to every variable for locking purposes"""
    count = 0
    # We want simple variables to have a lower id, such that they can be safely used in array indexing.
    for key, variable in sorted(c.name_to_variable.items(), key=lambda v: (v[1].type.size, v[0])):
        variable = c.name_to_variable[key]
        variable.lock_id = count
        if variable.type.size > 1:
            count += variable.type.size
        else:
            count += 1
    c.number_of_class_variables = count


#
#
#


def gather_used_variables(model):
    """Gather the variables that are used within the statements"""
    class_name = model.__class__.__name__
    if class_name in ["Assignment", "Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if model.right is None:
            return gather_used_variables(model.left)
        else:
            return gather_used_variables(model.left).union(gather_used_variables(model.right))
    elif class_name == "ExpressionRef":
        if model.index is None:
            return {(model.ref, None)}
        else:
            return {(model.ref, get_instruction(model.index))}
    elif class_name == "VariableRef":
        if model.index is None:
            return {(model.var.name, None)}
        else:
            # The index might also hide a variable within it. Account for these as well.
            return {(model.var.name, get_instruction(model.index))} | gather_used_variables(model.index)
    elif class_name == "Primary" and model.ref is not None:
        return gather_used_variables(model.ref)
    else:
        return set([])


def propagate_used_variables(model):
    """Propagate all the used variables throughout the model"""
    class_name = model.__class__.__name__
    if class_name == "Class":
        model.used_variables = set([])
        for sm in model.statemachines:
            model.used_variables |= propagate_used_variables(sm)
    elif class_name == "StateMachine":
        model.used_variables = set([])
        model.used_variables_per_state = {_s: set([]) for _s in model.states}
        for t in model.transitions:
            used_variables = propagate_used_variables(t)
            model.used_variables |= used_variables
            model.used_variables_per_state[t.source] |= used_variables
    elif class_name == "Transition":
        model.used_variables = propagate_used_variables(model.guard)
        for s in model.statements:
            model.used_variables |= propagate_used_variables(s)
    elif class_name == "Composite":
        model.used_variables = propagate_used_variables(model.guard)
        for a in model.assignments:
            model.used_variables |= propagate_used_variables(a)
    elif class_name in ["Assignment", "Expression"]:
        model.used_variables = gather_used_variables(model)
    else:
        model.used_variables = set([])

    # Always return a copy such that the original is never altered accidentally.
    return set(model.used_variables)


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


def propagate_lock_variables(model, class_variables):
    """For each Composite/Assignment/Expression, add the variables that have to be locked as a field"""
    class_name = model.__class__.__name__
    if class_name == "Class":
        for sm in model.statemachines:
            propagate_lock_variables(sm, class_variables)
        return
    elif class_name == "StateMachine":
        for t in model.transitions:
            propagate_lock_variables(t, class_variables)
        return
    elif class_name == "Transition":
        propagate_lock_variables(model.guard, class_variables)
        for s in model.statements:
            propagate_lock_variables(s, class_variables)
        return
    elif class_name == "Composite":
        model.lock_variables = propagate_lock_variables(model.guard, class_variables)
        for a in model.assignments:
            model.lock_variables |= propagate_lock_variables(a, class_variables)
    elif class_name == "Expression":
        # Expressions can be trivially satisfiable/unsatisfiable. If so, we don't need to lock.
        model.lock_variables = set([])
        if not model.is_trivially_satisfiable and not model.is_trivially_unsatisfiable:
            model.lock_variables |= {v for v in model.used_variables if v[0] in class_variables}
    elif class_name == "Assignment":
        model.lock_variables = {v for v in model.used_variables if v[0] in class_variables}
    else:
        model.lock_variables = set([])

    # Always return a copy such that the original is never altered accidentally.
    return set(model.lock_variables)


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
    t.statements = [transform_statement(_s) for _s in t.statements]

    # We determine whether a transition is guarded by looking whether the first statement is an expression.
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
    type(t).__repr__ = lambda self: "[%s -> %s] %s" % (
        self.source, self.target, "; ".join(v.__repr__() for v in [self.guard] + self.statements)
    )
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
        type(v).__repr__ = lambda v: "%s (%s)" % (v.name, (v.type.base if v.type.size == 0 else "%s[%s]" % (v.type.base, v.type.size)))


def transform_model(model):
    """Transform the model such that it provides all the data required for the code conversion"""
    for c in model.classes:
        c.name_to_variable = {v.name: v for v in c.variables}
        for sm in c.statemachines:
            transform_state_machine(sm, c)
        calculate_lock_ids(c)

        # Give the variables a readable representation.
        for v in c.variables:
            type(v).__repr__ = lambda v: "%s (%s)" % (v.name, (v.type.base if v.type.size == 0 else "%s[%s]" % (v.type.base, v.type.size)))

    # Check which variables have been used in the model and find all variables that need to be locked.
    for c in model.classes:
        propagate_used_variables(c)
        propagate_simplification(c)

        for sm in c.statemachines:
            get_ranges(sm)

        propagate_lock_variables(c, c.name_to_variable.keys())

    # Ensure that each class has references to its objects.
    for c in model.classes:
        c.objects = []
    for _o in model.objects:
        _o.type.objects.append(_o)

    return model
