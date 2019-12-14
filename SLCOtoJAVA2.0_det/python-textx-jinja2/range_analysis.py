import math


class Node:
    def __init__(self, value, variables):
        self.value = value
        # TODO the range might not be a single value--take the inverse of equals for example.
        self.range = {_v: TruthSet(-math.inf, math.inf) for _v in variables}
        self.successors = set([])

    def __repr__(self):
        return "%s %s" % (self.value, self.range)


class TruthSet:
    def __init__(self, lb=0., ub=0., ranges=None):
        """The given upper and lower bounds are always inclusive."""
        if ranges is not None:
            for lb, ub in ranges:
                assert lb <= ub
            self.ranges = ranges
        else:
            # The range is always inclusive.
            assert lb <= ub
            self.ranges = [(lb, ub)]

    def __repr__(self) -> str:
        return self.ranges.__repr__()

    def union(self, other):
        """Calculate the union between two truth sets"""
        if len(self.ranges) == 0 or len(other.ranges) == 0:
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
                if t > 1:
                    # Start merge at the current value.
                    current_start = v
            else:
                if t > 1:
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
    for _t in model.transitions:
        # Get the node object for the starting point.
        start_node = state_nodes[_t.source]

        # Create notes for all the statements in the transition.
        if len(_t.statements) > 0:
            statements = [_t.guard]
            if _t.statements[0].__class__.__name__ == "Composite":
                statements.extend(_t.statements[0].assignments)
            for statement in statements[1:]:
                if statement.__class__.__name__ == "Composite":
                    pass
                else:
                    pass


            # We also only consider variables that we are interested in.
            if _t.statements[0].__class__.__name__ == "Composite":
                pass
            else:
                # Create the split. Note that the false can take on many forms, with many different ranges!
                # We also only consider variables that we are interested in.
                pass
        else:
            # We may only have a guard, or a direct transition to another node.
            if _t.guard.smt is True:
                # We have no guard.
                start_node.successors.add(state_nodes[_t.target])
            else:
                # Create the split. Note that the false can take on many forms, with many different ranges!
                # We also only consider variables that we are interested in.
                pass
            pass

    # TODO guards should be split in a success and failure branch.

    pass


def get_ranges(model):
    """Given a model of a state machine, find the ranges of the local variables"""
    construct_control_flow_graph(model)
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


    pass
