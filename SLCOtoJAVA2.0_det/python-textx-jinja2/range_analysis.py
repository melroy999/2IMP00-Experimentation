import math
from queue import PriorityQueue

from smt_functions import to_simple_ast


class Node:
    def __init__(self, value, variables, decision=None):
        self.value = value
        self.ranges = {_v: TruthSet(-math.inf, math.inf) for _v in variables}
        self.successors = set([])
        self.predecessors = set([])
        self.decision = decision

    def __repr__(self):
        return ("%s %s %s" % ("" if self.decision is None else self.decision, self.value, self.ranges)).strip()

    def add_successor(self, value):
        self.successors.add(value)
        value.predecessors.add(self)




class TruthSet:
    def __init__(self, lb=0., ub=0., ranges=None):
        """The given upper and lower bounds are always inclusive."""
        if ranges is not None:
            for lb, ub in ranges:
                assert lb <= ub
            self.ranges = list(ranges)
        else:
            # The range is always inclusive.
            assert lb <= ub
            self.ranges = [(lb, ub)]

    def __repr__(self) -> str:
        return self.ranges.__repr__()

    def union(self, other, check_list_length=True):
        """Calculate the union between two truth sets"""
        if len(self.ranges) == 0 or check_list_length and len(other.ranges) == 0:
            return TruthSet(ranges=list(self.ranges + other.ranges))

        ranges = sorted(self.ranges + other.ranges)
        merged_ranges = []
        last_merge = ranges[0]
        for i in range(1, len(ranges)):
            # prev.ub >= next.lb
            if last_merge[1] >= ranges[i][0]:
                last_merge = (last_merge[0], max(last_merge[1], ranges[i][1]))
            else:
                merged_ranges.append(last_merge)
                last_merge = ranges[i]
        merged_ranges.append(last_merge)
        return TruthSet(ranges=merged_ranges)

    def intersect(self, other):
        """Calculate the intersection between two truth sets"""
        # We assume that the ranges are already flat.
        # Thus, overlaps will only occur if two ranges are active at the same time.
        # Moreover, we assume that the ranges are sorted before the call.
        # Convert the ranges to start and end points.
        if len(self.ranges) == 0 or len(other.ranges) == 0:
            return TruthSet(ranges=[])

        ranges = self.ranges + other.ranges
        events = []
        for lh, rh in ranges:
            events.extend([(lh, 0), (rh, 1)])
        nr_open_ranges = 0
        current_start = None
        intersected_ranges = []
        for v, t in sorted(events):
            if t == 0:
                nr_open_ranges += 1
                if nr_open_ranges > 1:
                    # Start merge at the current value.
                    current_start = v
            else:
                if nr_open_ranges > 1:
                    # Close the current range.
                    intersected_ranges.append((current_start, v))
                nr_open_ranges -= 1
        return TruthSet(ranges=intersected_ranges)

    def negate(self):
        """Negate the current truth set"""
        if len(self.ranges) == 0:
            return TruthSet(-math.inf, math.inf)

        ranges = []
        current_start = None
        for lb, ub in self.ranges:
            if lb > -math.inf:
                ranges.append((-math.inf, lb - 1))
            if current_start is not None:
                ranges.append((current_start, ub - 1))
            current_start = ub + 1
            if ub < math.inf:
                ranges.append((ub + 1, math.inf))

    def __eq__(self, o):
        # Two truth sets are equivalent of their ranges are equivalent.
        if self.__class__ != o.__class__:
            return False
        return self.ranges == o.ranges

    def __flatten(self):
        return self.union(TruthSet(ranges=[]), False)

    def add(self, o):
        return TruthSet(ranges=[(lb + lb2, ub + ub2) for lb2, ub2 in o.ranges for lb, ub in self.ranges]).__flatten()

    def subtract(self, o):
        return TruthSet(ranges=[(lb - lb2, ub - ub2) for lb2, ub2 in o.ranges for lb, ub in self.ranges]).__flatten()

    def multiply(self, o):
        return TruthSet(ranges=[(lb * lb2, ub * ub2) for lb2, ub2 in o.ranges for lb, ub in self.ranges]).__flatten()

    def divide(self, o):
        return TruthSet(ranges=[(lb / lb2, ub / ub2) for lb2, ub2 in o.ranges for lb, ub in self.ranges]).__flatten()



class ControlFlowGraph:
    def __init__(self, nodes, state_nodes, variables):
        self.nodes = nodes
        self.state_nodes = state_nodes
        self.variables = variables


def construct_control_flow_graph(model):
    # First, find the variables we are interested in.
    variables = []
    for _v in model.variables:
        if _v.type.base == "Integer":
            if _v.type.size > 0:
                variables.extend(["%s[%s]" % (_v.name, i) for i in range(0, _v.type.size)])
            else:
                variables.append(_v.name)

    # Next, start by creating graph nodes for every state in the model.
    state_nodes = {
        state: Node(state, variables) for state in model.states
    }

    # Create a node for each control point in the model and set the pointers appropriately.
    nodes = []
    for t in model.transitions:
        if t.is_trivially_unsatisfiable:
            false_node = Node(t.guard_expression, variables, False)
            nodes.append(false_node)
            state_nodes[t.source].add_successor(false_node)
            false_node.add_successor(state_nodes[t.source])
        else:
            # We need to add more nodes.
            last_node = state_nodes[t.source]
            if t.is_trivially_satisfiable:
                # Only create a true node.
                true_node = Node(t.guard_expression, variables, True)
                nodes.append(true_node)
                last_node.add_successor(true_node)
                last_node = true_node
            else:
                # Split the guard expression into a true and false group and give them infinite ranges.
                true_node = Node(t.guard_expression, variables, True)
                false_node = Node(t.guard_expression, variables, False)

                # Set the appropriate pointers.
                nodes.append(true_node)
                nodes.append(false_node)
                last_node.add_successor(true_node)
                last_node.add_successor(false_node)
                false_node.add_successor(state_nodes[t.source])
                last_node = true_node

                # The guard might be a composite. Create the appropriate chain of assignments if that is the case.
                if t.guard.__class__.__name__ == "Composite":
                    for a in t.guard.assignments:
                        current_node = Node(a, variables)
                        nodes.append(current_node)
                        last_node.add_successor(current_node)
                        last_node = current_node

            # Process the statements next.
            for s in t.statements:
                class_name = s.__class__.__name__
                if class_name == "Expression":
                    if s.is_trivially_satisfiable:
                        # Only create a true node.
                        true_node = Node(s, variables, True)
                        nodes.append(true_node)
                        last_node.add_successor(true_node)
                        last_node = true_node
                    else:
                        # Split the guard expression into a true and false group and give them infinite ranges.
                        true_node = Node(s, variables, True)
                        false_node = Node(s, variables, False)

                        # Set the appropriate pointers.
                        nodes.append(true_node)
                        nodes.append(false_node)
                        last_node.add_successor(true_node)
                        last_node.add_successor(false_node)
                        false_node.add_successor(state_nodes[t.source])
                        last_node = true_node

                elif class_name == "Composite":
                    if s.is_trivially_satisfiable:
                        # Only create a true node.
                        true_node = Node(s.guard, variables, True)
                        nodes.append(true_node)
                        last_node.add_successor(true_node)
                        last_node = true_node
                    else:
                        # Split the guard expression into a true and false group and give them infinite ranges.
                        true_node = Node(s.guard, variables, True)
                        false_node = Node(s.guard, variables, False)

                        # Set the appropriate pointers.
                        nodes.append(true_node)
                        nodes.append(false_node)
                        last_node.add_successor(true_node)
                        last_node.add_successor(false_node)
                        false_node.add_successor(state_nodes[t.source])
                        last_node = true_node

                        for a in t.guard.assignments:
                            current_node = Node(a, variables)
                            nodes.append(current_node)
                            last_node.add_successor(current_node)
                            last_node = current_node

                else:
                    # The node is a simple assignment.
                    current_node = Node(s, variables)
                    nodes.append(current_node)
                    last_node.add_successor(current_node)
                    last_node = current_node

            # Finalize the chain.
            last_node.add_successor(state_nodes[t.target])

    # Create a class wrapper for the control flow graph.
    return ControlFlowGraph(nodes + list(state_nodes.values()), state_nodes, variables)


def get_variable_names(ops, ranges):
    if len(ops) == 1:
        return [v for v in [ops[0]] if v in ranges]
    else:
        try:
            return [v for v in ["%s[%s]" % (ops[0], int(ops[1]))] if v in ranges]
        except TypeError:
            # TODO only select the appropriate variables, instead of all, using the ranges.
            return [k for k in ranges.keys() if k.startswith(ops[0]) and k in ranges]


def apply_assignment(ast, ranges):
    # Base types can be returned as-is.
    if type(ast) == int:
        return TruthSet(ast, ast)

    operator, ops = ast[0], ast[1:]
    if operator.startswith("var"):
        target_variables = get_variable_names(ops, ranges)

        if len(target_variables) == 0:
            return TruthSet(-math.inf, math.inf)
        else:
            current_range = ranges.get(target_variables[0], TruthSet(-math.inf, math.inf))
            for k in target_variables[1:]:
                current_range = current_range.union(ranges.get(k, TruthSet(-math.inf, math.inf)))
            return current_range

    if len(ops) == 2:
        lhs = apply_assignment(ops[0], ranges)
        rhs = apply_assignment(ops[1], ranges)

        if operator == "+":
            return lhs.add(rhs)
        if operator == "-":
            return lhs.subtract(rhs)
        if operator == "*":
            return lhs.multiply(rhs)
        if operator == "/":
            return lhs.divide(rhs)
        if operator == "%":
            # A remainder operation limits the result to the value of the right hand side.
            # TODO this is done simplistic right now--the range is dictated by the rhs, without observing the lhs.
            rhs_min = rhs.ranges[0][0]
            rhs_max = rhs.ranges[-1][1]
            remainder_range = max(-rhs_min, rhs_max)
            return TruthSet(-remainder_range, remainder_range)



    # Power operator.
    if operator == "**":
        pass

        pass

    # Unary operators.
    if len(ops) == 1:
        pass

    # Fallback for remaining cases.
    raise Exception("Range deduction not possible for operator {%s}." % operator)


def apply_test(ast, ranges, true_branch):
    if type(ast) in [int, bool, float, str]:
        return ranges

    operator, ops = ast[0], ast[1:]

    # if operator == "and":
    #     # TODO this is not correct. The function returns a dict, since multiple variables might be at play.
    #     return apply_test(ops[0], ranges).intersect(apply_test(ops[1], ranges))
    # if operator == "or":
    #     return apply_test(ops[0], ranges).union(apply_test(ops[1], ranges))
    # if operator == "xor":
    #     raise Exception("XOR is not yet implemented")
    # if operator == "not":
    #     lhs = apply_assignment(ops[0], ranges)
    #     return lhs.negate()

    # TODO: assuming that lhs and rhs are mathematical expressions.
    lhs = apply_assignment(ops[0], ranges)
    rhs = apply_assignment(ops[1], ranges)

    # Check if either of the two sides is a variable.
    lhs_variables = []
    if type(ops[0]) is not int and ops[0][0].startswith("var"):
        lhs_variables = get_variable_names(ops[0][1:], ranges)
    rhs_variables = []
    if type(ops[1]) is not int and ops[1][0].startswith("var"):
        rhs_variables = get_variable_names(ops[1][1:], ranges)

    if operator == "=":
        # TODO inverse
        result_dict = {}
        for v in lhs_variables:
            result_dict[v] = ranges[v].intersect(rhs)
        for v in rhs_variables:
            result_dict[v] = ranges[v].intersect(lhs)
        return {**ranges, **result_dict}
    if (true_branch and operator == "<") or (not true_branch and operator == ">="):
        result_dict = {}
        for v in lhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(-math.inf, rhs.ranges[-1][1] - 1))
        for v in rhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(lhs.ranges[0][0] + 1, math.inf))
        return {**ranges, **result_dict}
    if (true_branch and operator == "<=") or (not true_branch and operator == ">"):
        result_dict = {}
        for v in lhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(-math.inf, rhs.ranges[-1][1]))
        for v in rhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(lhs.ranges[0][0], math.inf))
        return {**ranges, **result_dict}
    if (true_branch and operator == ">") or (not true_branch and operator == "<="):
        result_dict = {}
        for v in lhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(rhs.ranges[0][0] + 1, math.inf))
        for v in rhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(-math.inf, lhs.ranges[-1][1] - 1))
        return {**ranges, **result_dict}
    if (true_branch and operator == ">=") or (not true_branch and operator == "<"):
        result_dict = {}
        for v in lhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(rhs.ranges[0][0], math.inf))
        for v in rhs_variables:
            result_dict[v] = ranges[v].intersect(TruthSet(-math.inf, lhs.ranges[-1][1]))
        return {**ranges, **result_dict}

    # Fallback for remaining cases.
    raise Exception("Range deduction not possible for operator {%s}." % operator)


def get_default_variable_value(model):
    """ return default value for given variable """
    if model.defvalue is not None:
        return model.defvalue
    elif len(model.defvalues) > 0:
        return [v for v in model.defvalues]
    elif model.type.base in ["Integer", "Byte"]:
        return 0 if model.type.size < 1 else [0 for _ in range(0, model.type.size)]
    elif model.type.base == "Boolean":
        return True if model.type.size < 1 else [True for _ in range(0, model.type.size)]


def range_propagation(cfg, model):
    """Perform range propagation on the given control flow graph"""
    # First, assign the initial values for the used variables in the starting state.
    starting_node = cfg.state_nodes[model.initialstate]
    for v in model.variables:
        if v.type.size == 0:
            default_value = get_default_variable_value(v)
            starting_node.ranges[v.name] = TruthSet(default_value, default_value)
        else:
            default_variables = get_default_variable_value(v)
            for i, value in enumerate(default_variables):
                starting_node.ranges["%s[%s]" % (v.name, i)] = TruthSet(value, value)

    queue = set(cfg.nodes)
    while len(queue) > 0:
        # Take an arbitrary node from the queue to process.
        target_node = queue.pop()

        # Get the type of the node and choose the propagation accordingly.
        type_name = target_node.value.__class__.__name__
        predecessors = list(target_node.predecessors)

        if type_name == "str":
            # Take the union of all predecessor values and check if the range has become narrower.
            # We assume that a predecessor always exists.
            assert len(predecessors) > 0

            # Copy the values of the first predecessor.
            new_ranges = {
                k: v for k, v in predecessors[0].ranges.items()
            }

            # Take the union of all the other ranges.
            for predecessor in predecessors[1:]:
                for k, v in predecessor.ranges.items():
                    new_ranges[k] = v.union(new_ranges[k])

            # Check if any of the ranges have changed.
            if target_node.ranges != new_ranges:
                target_node.ranges = new_ranges
                queue.update(target_node.successors)
        elif type_name == "Assignment":
            # Which value is granted to us by our single predecessor? (statements always have one predecessor)
            assert len(target_node.predecessors) == 1
            predecessor = predecessors[0]

            # What is the target variable of the assignment?
            variable_ref = to_simple_ast(target_node.value.left)
            if variable_ref[0] == "var":
                target_variables = [variable_ref[1]]
            else:
                try:
                    target_variables = ["%s[%s]" % (variable_ref[1], int(variable_ref[2]))]
                except TypeError:
                    # TODO only select the appropriate variables, instead of all, using the ranges.
                    target_variables = [v for v in cfg.variables if v.startswith(variable_ref[1])]

            # Apply the new assignment.
            # TODO make the assignment smarter--it might occur that both sides use the assignment use the same index.
            assignment = to_simple_ast(target_node.value.right)
            range_result = apply_assignment(assignment, predecessor.ranges)

            # Copy the values of the first predecessor and apply the value changes.
            new_ranges = {
                k: v for k, v in predecessor.ranges.items()
            }

            # Check if the target variables have changed.
            for v in target_variables:
                if v in cfg.variables:
                    new_ranges[v] = range_result

            # Check if any of the ranges have changed.
            if target_node.ranges != new_ranges:
                target_node.ranges = new_ranges
                queue.update(target_node.successors)

        elif type_name == "Expression":
            # Which value is granted to us by our single predecessor? (statements always have one predecessor)
            assert len(target_node.predecessors) == 1

            predecessor = predecessors[0]
            new_ranges = apply_test(target_node.value.smt, predecessor.ranges, target_node.decision)

            # Check if any of the ranges have changed.
            if target_node.ranges != new_ranges:
                target_node.ranges = new_ranges
                queue.update(target_node.successors)


def get_ranges(model):
    """Given a model of a state machine, find the ranges of the local variables"""
    cfg = construct_control_flow_graph(model)
    range_propagation(cfg, model)

    # variables = []
    # for _v in model.variables:
    #     if _v.type.base == "Integer":
    #         if _v.type.size > 0:
    #             variables.extend(["%s[%s]" % (_v.name, i) for i in range(0, _v.type.size)])
    #         else:
    #             variables.append(_v.name)
    #
    # # The initial ranges of variables are infinite.
    # ranges = {
    #     _v: (-math.inf, math.inf) for _v in variables
    # }
    #
    # # Construct a control-flow graph.
    # # TODO: Simple naive idea: start by checking if there are + or - operations to see if infinite growth exists.
    return cfg

    pass
