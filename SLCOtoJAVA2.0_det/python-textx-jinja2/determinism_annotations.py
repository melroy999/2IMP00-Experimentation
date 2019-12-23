from enum import Enum

import settings
from smt_functions import to_smt_format_string, z3_opr_check


def print_decision_groups(tree, d=1):
    """Print the decision hierarchy with tab indents"""
    if tree.__class__.__name__ == "Transition":
        print("%s- %s" % ("\t" * d, tree))
    else:
        choice_type, members = tree
        print("%s- %s" % ("\t" * d, choice_type))
        for t in sorted(members, key=lambda v: v.__class__.__name__ != "Transition"):
            print_decision_groups(t, d + 1)


def print_determinism_report(state, sm, transitions, trivially_satisfiable, trivially_unsatisfiable):
    """Print a formatted report of the decision structure for the given state"""
    print("#" * 120)
    print("State Machine:", sm.name)
    print("State:", state)
    print()
    report_trivially_satisfiable = [
        t for t in trivially_satisfiable if t.guard_expression.smt is not True
    ]
    if len(report_trivially_satisfiable) > 0:
        print("WARNING: The following transition guards hold vacuously TRUE:")
        for t in report_trivially_satisfiable:
            print("\t- %s" % t)
        print()
    if len([t for t in trivially_unsatisfiable]) > 0:
        print("WARNING: The following transition guards are always FALSE:")
        for t in [t for t in trivially_unsatisfiable]:
            print("\t- %s" % t)
        print()
    print("Transitions:")
    for t in transitions:
        print("\t- %s" % t)
    print()
    print("Decisions:")
    print_decision_groups(sm.groupings[state])
    print("#" * 120)
    print()


class Decision(Enum):
    """A simple enum that denotes whether a decision is made deterministically or non-deterministically"""
    DET = 0
    N_DET = 1

    def __repr__(self):
        return self.__str__()


def dissect_overlapping_transition_chain(transitions, variables, truth_matrices):
    """Dissect a list of transitions with a non-interrupted chain of overlap"""
    if len(transitions) == 1:
        return transitions[0]

    # Example input:
    # x -------    --------
    # y     --------

    # Not allowed:
    # x -------
    # y            -------

    # Find the variables that are used in the transitions and group based on the chosen variables.
    variables_to_transitions = {}
    for t in transitions:
        _, used_variables = to_smt_format_string(t.guard_expression.smt)
        variables_to_transitions.setdefault(frozenset(used_variables.keys()), []).append(t)

    # Check if the groups can be split up more.
    groupings = [find_deterministic_groups(v, variables, truth_matrices) for v in variables_to_transitions.values()]

    # The split needs to be resolved non-deterministically.
    return (Decision.N_DET, groupings) if len(groupings) > 1 else groupings[0]


def group_overlapping_transitions(transitions, variables, and_truth_matrix):
    """Divide the transitions into groups, based on the equality measure"""
    if len(transitions) == 1:
        return transitions[0]

    # Transitions are in the same group if they have an equality relation with one another.
    groupings = []

    processed_transitions = set()
    queue = set()
    for t in transitions:
        if t not in processed_transitions:
            # Find all transitions that have an equality relation with this _t.
            queue.update([t2 for t2 in transitions if and_truth_matrix[t][t2]])

            current_group_transitions = []

            while len(queue) > 0:
                t2 = queue.pop()

                if t2 not in processed_transitions:
                    # Add the transition to the current group.
                    current_group_transitions += [t2]

                    # Find all transitions that are related to _t.
                    queue.update([t3 for t3 in transitions if and_truth_matrix[t2][t3]])

                    # We do not want to visit the queue head again.
                    processed_transitions.add(t2)

            if len(current_group_transitions) > 0:
                # Can the found list of groupings be dissected further?
                sub_groupings = dissect_overlapping_transition_chain(
                    current_group_transitions, variables, and_truth_matrix
                )

                # Add the group to the list of groupings.
                groupings += [sub_groupings]

    # The result is always deterministic.
    return (Decision.DET, groupings) if len(groupings) > 1 else groupings[0]


def find_deterministic_groups(transitions, _vars, and_truth_matrix):
    """Find groups that are deterministic in regards to one another"""
    # Check whether we have a list of transitions to dissect.
    if len(transitions) <= 1:
        return Decision.DET, transitions

    # Do any of the transitions always possibly overlap with the others transitions?
    # Keep in mind that the truth table has all transitions--only select those that we are examining.
    invariably_overlapping_transitions = [
        t for t in transitions if all(
            and_truth_matrix[t][t2] for t2 in transitions
        )
    ]

    # If we have several invariably active transitions, but not all transitions are, divide and conquer.
    if len(invariably_overlapping_transitions) == 0:
        # Dissect the group of transitions and find a way to split if possible.
        return group_overlapping_transitions(transitions, _vars, and_truth_matrix)
    else:
        # Find the transitions that are not invariably active.
        remaining_transitions = [t for t in transitions if t not in invariably_overlapping_transitions]

        # Recursively solve for the non invariably overlapping transitions.
        if len(remaining_transitions) > 0:
            remaining_groupings = [find_deterministic_groups(remaining_transitions, _vars, and_truth_matrix)]
        else:
            remaining_groupings = []

        # The resulting sub-grouping is to be processed in parallel with the invariably active transitions.
        choices = invariably_overlapping_transitions + remaining_groupings
        return (Decision.N_DET, choices) if len(choices) > 1 else choices[0]


def format_decision_group_tree(tree, trivially_satisfiable_transitions):
    """Compress the decision group tree such that the decision type alternates per level"""
    if tree.__class__.__name__ == "Transition":
        return tree
    else:
        choice_type, members = tree
        compressed_members = []
        for m in members:
            m = format_decision_group_tree(m, trivially_satisfiable_transitions)

            if m.__class__.__name__ == "Transition":
                if choice_type == Decision.N_DET:
                    if m in trivially_satisfiable_transitions:
                        compressed_members.append(m)
                    else:
                        compressed_members.append((Decision.DET, [m]))
                else:
                    compressed_members.append(m)
            else:
                if m[0] != choice_type:
                    compressed_members.append(m)
                else:
                    compressed_members.extend(m[1])

        return choice_type, compressed_members


def calculate_and_truth_matrix(transitions, variables):
    """Calculate the truth matrices for the transitions"""
    truth_matrix = {}
    for t in transitions:
        truth_matrix[t] = {}
        for t2 in transitions:
            truth_evaluation = z3_opr_check("and", t.guard_expression.smt, t2.guard_expression.smt, variables, False)
            truth_matrix[t][t2] = truth_evaluation
            if t == t2:
                break
            truth_matrix[t2][t] = truth_evaluation
    return truth_matrix


def add_determinism_annotations(model):
    """Observe the transitions in the model and determine which can be done deterministically"""
    for c in model.classes:
        for sm in c.statemachines:
            sm.groupings = {s: None for s in sm.adjacency_list.keys()}

            for state, transitions in sm.adjacency_list.items():
                variables = {**c.name_to_variable, **sm.name_to_variable}

                if len(transitions) > 0:
                    # Are there transitions that are trivially (un)satisfiable?
                    trivially_satisfiable = [t for t in transitions if t.is_trivially_satisfiable]
                    trivially_unsatisfiable = [t for t in transitions if t.is_trivially_unsatisfiable]

                    # Find the transitions that remain.
                    solved_transitions = trivially_satisfiable + trivially_unsatisfiable
                    remaining_transitions = [t for t in transitions if t not in solved_transitions]

                    # Create the truth matrices for the AND, XOR and implication operators.
                    and_truth_matrix = calculate_and_truth_matrix(remaining_transitions, variables)

                    sub_groupings = []
                    if len(remaining_transitions) > 0:
                        sub_groupings += [find_deterministic_groups(remaining_transitions, variables, and_truth_matrix)]

                    choices = trivially_satisfiable + sub_groupings
                    if len(choices) == 0:
                        continue

                    groupings = (Decision.N_DET, choices) if len(choices) > 1 else choices[0]
                    sm.groupings[state] = format_decision_group_tree(groupings, trivially_satisfiable)

                    if settings.print_decision_report:
                        print_determinism_report(state, sm, transitions, trivially_satisfiable, trivially_unsatisfiable)
    return model
