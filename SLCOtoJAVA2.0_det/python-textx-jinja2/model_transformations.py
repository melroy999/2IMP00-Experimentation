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


class Node:
    def __init__(self, key):
        self.predecessors = set([])
        self.successors = set([])
        self.key = key
        self.max_no_successors = 0

    def __repr__(self):
        return "%s" % self.key

    def add_successor(self, value):
        self.successors.add(value)
        self.max_no_successors = len(self.successors)
        value.predecessors.add(self)


def construct_variable_dependency_graph(model, variable_to_node, variable_stack=None):
    if variable_stack is None:
        variable_stack = []
    if model is None:
        return

    class_name = model.__class__.__name__
    if class_name == "Transition":
        construct_variable_dependency_graph(model.guard, variable_to_node, variable_stack)
        for s in model.statements:
            construct_variable_dependency_graph(s, variable_to_node, variable_stack)
    elif class_name == "Composite":
        construct_variable_dependency_graph(model.guard, variable_to_node, variable_stack)
        for a in model.assignments:
            construct_variable_dependency_graph(a, variable_to_node, variable_stack)
    elif class_name == "ExpressionRef":
        if len(variable_stack) > 0 and model.ref in variable_to_node:
            target_variable = variable_to_node[model.ref]
            parent_variable = variable_to_node[variable_stack[-1]]
            parent_variable.add_successor(target_variable)
        variable_stack.append(model.ref)
        construct_variable_dependency_graph(model.index, variable_to_node, variable_stack)
        variable_stack.pop()
    elif class_name == "VariableRef":
        if len(variable_stack) > 0 and model.var.name in variable_to_node:
            target_variable = variable_to_node[model.var.name]
            parent_variable = variable_to_node[variable_stack[-1]]
            parent_variable.add_successor(target_variable)
        variable_stack.append(model.var.name)
        construct_variable_dependency_graph(model.index, variable_to_node, variable_stack)
        variable_stack.pop()
    elif class_name == "Primary":
        construct_variable_dependency_graph(model.body, variable_to_node, variable_stack)
        construct_variable_dependency_graph(model.ref, variable_to_node, variable_stack)
        construct_variable_dependency_graph(model.value, variable_to_node, variable_stack)
    elif class_name in ["Assignment", "Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        construct_variable_dependency_graph(model.left, variable_to_node, variable_stack)
        construct_variable_dependency_graph(model.right, variable_to_node, variable_stack)


def assign_lock_ids(model):
    """Assign lock ids to every class variable, using a dependency graph"""
    # First, create nodes for every variable we are interested in.
    variable_to_node = {v: Node(v) for v in model.name_to_variable.keys()}

    # Create a dependency graph, where a variable x depends on y if it is used in the index of x.
    for sm in model.statemachines:
        for t in sm.transitions:
            construct_variable_dependency_graph(t, variable_to_node)

    to_assign = set(variable_to_node.keys())
    counter = 0
    while len(to_assign) > 0:
        # Lock ids are granted first to the leaves in the graph.
        # Continue until no more leaves can be found.
        while any(len(variable_to_node[v].successors) == 0 for v in to_assign):
            for v in sorted(list(to_assign), key=lambda _v: (variable_to_node[_v].max_no_successors, _v)):
                target_node = variable_to_node[v]
                if len(target_node.successors) == 0:
                    variable = model.name_to_variable[v]
                    variable.lock_id = counter
                    to_assign.discard(v)

                    # Remove the association of the predecessor nodes to the target node.
                    for node in target_node.predecessors:
                        node.successors.discard(target_node)

                    # Determine the next id to use.
                    if variable.type.size > 1:
                        counter += variable.type.size
                    else:
                        counter += 1

        # No more leaves can be found, implying a circular reference.
        # Process the node that depends on the fewest other nodes first.
        remaining_variables = sorted(list(to_assign), key=lambda _v: (variable_to_node[_v].max_no_successors, _v))
        if len(remaining_variables) > 0:
            v = remaining_variables[0]
            target_node = variable_to_node[v]
            variable = model.name_to_variable[v]
            variable.lock_id = counter
            to_assign.discard(v)

            # Remove any existing self-references.
            target_node.predecessors.discard(target_node)

            # Remove the association of the predecessor nodes to the target node.
            for node in target_node.predecessors:
                node.successors.discard(target_node)
                node.predecessors.discard(target_node)

            # Determine the next id to use.
            if variable.type.size > 1:
                counter += variable.type.size
            else:
                counter += 1

    model.number_of_class_variables = counter


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
    # type(t).__repr__ = lambda self: "from %s to %s {%s}" % (
    #     self.source, self.target, "; ".join(v.__repr__() for v in [self.guard] + self.statements)
    # )

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
        propagate_used_variables(c)
        propagate_simplification(c)
        assign_lock_ids(c)
        propagate_lock_variables(c, c.name_to_variable.keys())

    # Ensure that each class has references to its objects.
    for c in model.classes:
        c.objects = []
    for _o in model.objects:
        _o.type.objects.append(_o)

    return model
