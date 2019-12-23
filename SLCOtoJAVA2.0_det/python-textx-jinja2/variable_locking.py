from java_instruction_conversion import get_instruction


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
            # The index might also hide a variable within it. Account for these as well.
            return {(model.ref, get_instruction(model.index))} | gather_used_variables(model.index)
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


class Node:
    """A simple node class used in the adjacency graph"""
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

    def remove_successor(self, value):
        self.successors.discard(value)
        value.predecessors.discard(self)

    def remove_predecessor(self, value):
        self.predecessors.discard(value)
        value.successors.discard(self)


def construct_variable_dependency_graph(model, variable_to_node, target_variables, variable_stack=None):
    """Construct a variable dependency graph, where a variable depends on another if it is used in the index"""
    if variable_stack is None:
        variable_stack = []
    if model is None:
        return

    class_name = model.__class__.__name__
    if class_name == "Transition":
        construct_variable_dependency_graph(model.guard, variable_to_node, target_variables, variable_stack)
        for s in model.statements:
            construct_variable_dependency_graph(s, variable_to_node, target_variables, variable_stack)
    elif class_name == "Composite":
        construct_variable_dependency_graph(model.guard, variable_to_node, target_variables, variable_stack)
        for a in model.assignments:
            construct_variable_dependency_graph(a, variable_to_node, target_variables, variable_stack)
    elif class_name == "ExpressionRef":
        if model.ref in target_variables:
            target_variable = variable_to_node.setdefault(model.ref, Node(model.ref))
            if len(variable_stack) > 0:
                parent_variable = variable_to_node.setdefault(variable_stack[-1], Node(variable_stack[-1]))
                parent_variable.add_successor(target_variable)
            variable_stack.append(model.ref)
        construct_variable_dependency_graph(model.index, variable_to_node, target_variables, variable_stack)
        if model.ref in target_variables:
            variable_stack.pop()
    elif class_name == "VariableRef":
        if model.var.name in target_variables:
            target_variable = variable_to_node.setdefault(model.var.name, Node(model.var.name))
            if len(variable_stack) > 0:
                parent_variable = variable_to_node.setdefault(variable_stack[-1], Node(variable_stack[-1]))
                parent_variable.add_successor(target_variable)
            variable_stack.append(model.var.name)
        construct_variable_dependency_graph(model.index, variable_to_node, target_variables, variable_stack)
        if model.var.name in target_variables:
            variable_stack.pop()
    elif class_name == "Primary":
        construct_variable_dependency_graph(model.body, variable_to_node, target_variables, variable_stack)
        construct_variable_dependency_graph(model.ref, variable_to_node, target_variables, variable_stack)
        construct_variable_dependency_graph(model.value, variable_to_node, target_variables, variable_stack)
    elif class_name in ["Assignment", "Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        construct_variable_dependency_graph(model.left, variable_to_node, target_variables, variable_stack)
        construct_variable_dependency_graph(model.right, variable_to_node, target_variables, variable_stack)


def assign_lock_ids_to_class_variables(model):
    """Assign lock ids to every class variable, using a dependency graph"""
    # First, create nodes for every variable we are interested in.
    variable_to_node = {}

    # Create a dependency graph, where a variable x depends on y if it is used in the index of x.
    for sm in model.statemachines:
        for t in sm.transitions:
            construct_variable_dependency_graph(t, variable_to_node, set(model.name_to_variable.keys()))

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


def order_lock_ids(v, name_to_variable):
    """Get the lock id of the given variable, used for sorting purposes"""
    variable, index = v
    try:
        offset = int(index)
    except (ValueError, TypeError):
        offset = 0
    return name_to_variable[variable].lock_id + offset


def correct_dependency_graph(variable_dependency_graph, name_to_variable, lock_ids=None):
    """Remove all dependencies that violate the lock id ordering, and decompose array lock requests when appropriate."""
    # If a node has a dependency on a higher id node, remove all dependencies of the node.
    # Remove superfluous lock id statements--all original lock id statements starting with the variable are superfluous.
    for node in variable_dependency_graph.values():
        target_variable = name_to_variable[node.key]
        if any(name_to_variable[v.key].lock_id >= target_variable.lock_id for v in node.successors):
            if lock_ids is not None:
                # Remove all lock id statements that are over variable node.key.
                lock_ids.symmetric_difference_update(set(v for v in lock_ids if v[0] == node.key))

                # Create lock ids for all values of the variable associated to the node.
                lock_ids.update((node.key, i) for i in range(0, target_variable.type.size))

            # Remove all dependencies of the node.
            for successor_node in list(node.successors):
                node.remove_successor(successor_node)


def get_locking_phases(variable_dependency_graph, name_to_variable, lock_ids):
    """Convert the list of lock ids to locking phases, adhering to the given dependency graph"""
    # Break the lock id list into different phases, following the dependency graph.
    lock_id_ordering = sorted(lock_ids, key=lambda v: order_lock_ids(v, name_to_variable))
    lock_variable_phases = []
    current_phase = []
    encountered_nodes = set([])
    for variable, index in lock_id_ordering:
        # Find the node associated with the variable.
        target_node = variable_dependency_graph[variable]

        # If the node has any successors, we need to move on to the next phase.
        # Note that no circular dependencies exist anymore, since the graph now has a strict lock id order.
        if len(target_node.successors) > 0:
            # Flush the current phase.
            lock_variable_phases.append(current_phase)
            current_phase = []

            # Remove all associations with the previously encountered nodes.
            for node in encountered_nodes:
                for predecessor_node in list(node.predecessors):
                    node.remove_predecessor(predecessor_node)

        # Add the variable nad index to the current phase.
        current_phase.append((variable, index))
        encountered_nodes.add(target_node)

    # Flush the last phase, if it is non-empty.
    if len(current_phase) > 0:
        lock_variable_phases.append(current_phase)
    return lock_variable_phases


def add_lock_ordering_corrections(model, name_to_variable):
    """Correct the ordering by removing circular dependencies that violate the lock id ordering,
    and convert the list of locks to phase system such that locks depending on variable values
    are only requested once said dependency is locked"""
    # Construct a variable dependency graph for the statement.
    variable_dependency_graph = {}
    construct_variable_dependency_graph(model, variable_dependency_graph, set(name_to_variable.keys()))

    # If a node has a dependency on a higher id node, expand and remove all dependencies of the node.
    correct_dependency_graph(variable_dependency_graph, name_to_variable, model.lock_variables)

    # Break the lock id list into different phases, following the dependency graph.
    model.lock_variable_phases = get_locking_phases(variable_dependency_graph, name_to_variable, model.lock_variables)


def construct_valid_lock_order(model):
    """Construct a phased lock ordering for all transitions in the given class"""
    for sm in model.statemachines:
        for t in sm.transitions:
            add_lock_ordering_corrections(t.guard, model.name_to_variable)
            for s in t.statements:
                add_lock_ordering_corrections(s, model.name_to_variable)
