# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object
# import libraries
import jinja2
import os

from enum import Enum
from jinja2_filters import *
from model_transformations import transform_model
from slcolib import *
from smt_helper_functions import *

this_folder = dirname(__file__)


class Decision(Enum):
    DET = 0
    N_DET = 1

    def __repr__(self):
        return self.__str__()


def dissect_overlapping_transition_chain(transitions, _vars, truth_matrices):
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
    for _t in transitions:
        _, _used_variables = to_smt_format_string(_t.guard.smt)
        variables_to_transitions.setdefault(frozenset(_used_variables.keys()), []).append(_t)

    # Check if the groups can be split up more.
    groupings = [find_deterministic_groups(_v, _vars, truth_matrices) for _v in variables_to_transitions.values()]

    # The split needs to be resolved non-deterministically.
    return (Decision.N_DET, groupings) if len(groupings) > 1 else groupings[0]


def group_overlapping_transitions(transitions, _vars, truth_matrices):
    """Divide the transitions into groups, based on the equality measure"""
    if len(transitions) == 1:
        return transitions[0]

    # Transitions are in the same group if they have an equality relation with one another.
    groupings = []

    processed_transitions = set()
    queue = set()
    for _t in transitions:
        if _t not in processed_transitions:
            # Find all transitions that have an equality relation with this _t.
            queue.update([_t2 for _t2 in transitions if truth_matrices["and"][_t][_t2]])

            current_group_transitions = []

            while len(queue) > 0:
                _t2 = queue.pop()

                if _t2 not in processed_transitions:
                    # Add the transition to the current group.
                    current_group_transitions += [_t2]

                    # Find all transitions that are related to _t.
                    queue.update([_t3 for _t3 in transitions if truth_matrices["and"][_t2][_t3]])

                    # We do not want to visit the queue head again.
                    processed_transitions.add(_t2)

            if len(current_group_transitions) > 0:
                # Can the found list of groupings be dissected further?
                sub_groupings = dissect_overlapping_transition_chain(current_group_transitions, _vars, truth_matrices)

                # Add the group to the list of groupings.
                groupings += [sub_groupings]

    # The result is always deterministic.
    return (Decision.DET, groupings) if len(groupings) > 1 else groupings[0]


def find_deterministic_groups(transitions, _vars, truth_matrices):
    """Find groups that are deterministic in regards to one another"""
    # Check whether we have a list of transitions to dissect.
    if len(transitions) <= 1:
        return Decision.DET, transitions

    # Do any of the transitions always possibly overlap with the others transitions?
    # Keep in mind that the truth table has all transitions--only select those that we are examining.
    invariably_overlapping_transitions = [
        _t for _t in transitions if all(
            truth_matrices["and"][_t][_t2] for _t2 in transitions
        )
    ]

    # If we have several invariably active transitions, but not all transitions are, divide and conquer.
    if len(invariably_overlapping_transitions) == 0:
        # Dissect the group of transitions and find a way to split if possible.
        return group_overlapping_transitions(transitions, _vars, truth_matrices)
    else:
        # Find the transitions that are not invariably active.
        remaining_transitions = [_t for _t in transitions if _t not in invariably_overlapping_transitions]

        # Recursively solve for the non invariably overlapping transitions.
        if len(remaining_transitions) > 0:
            remaining_groupings = [find_deterministic_groups(remaining_transitions, _vars, truth_matrices)]
        else:
            remaining_groupings = []

        # The resulting sub-grouping is to be processed in parallel with the invariably active transitions.
        choices = invariably_overlapping_transitions + remaining_groupings
        return (Decision.N_DET, choices) if len(choices) > 1 else choices[0]


def print_decision_groups(tree, d=1):
    if tree.__class__.__name__ == "Transition":
        print("%s%s" % ("\t" * d, tree))
    else:
        choice_type, members = tree
        print("%s%s" % ("\t" * d, choice_type))
        for _t in sorted(members, key=lambda _t: _t.__class__.__name__ != "Transition"):
            print_decision_groups(_t, d + 1)


def format_decision_group_tree(tree, vacuously_active_transitions):
    """Compress the decision group tree such that the decision type alternates per level"""
    if tree.__class__.__name__ == "Transition":
        return tree
    else:
        choice_type, members = tree

        compressed_members = []
        for _m in members:
            _m = format_decision_group_tree(_m, vacuously_active_transitions)

            if _m.__class__.__name__ == "Transition":
                if choice_type == Decision.N_DET:
                    if _m in vacuously_active_transitions:
                        compressed_members.append(_m)
                    else:
                        compressed_members.append((Decision.DET, [_m]))
                else:
                    compressed_members.append(_m)
            else:
                if _m[0] != choice_type:
                    compressed_members.append(_m)
                else:
                    compressed_members.extend(_m[1])

        return choice_type, compressed_members


def add_determinism_annotations(model):
    """Observe the transitions in the model and determine which can be done deterministically"""
    for _c in model.classes:
        for _sm in _c.statemachines:
            _sm.groupings = {_s: None for _s in _sm.adjacency_list.keys()}

            for _s, transitions in _sm.adjacency_list.items():
                _vars = {**_c.name_to_variable, **_sm.name_to_variable}

                if len(transitions) > 0:
                    # Are there transitions that are trivially unsatisfiable?
                    trivially_unsatisfiable = [
                        _t for _t in transitions if not do_z3_truth_check(_t.guard.smt, _vars, False)
                    ]

                    # Check if any of the transitions are trivially satisfiable.
                    trivially_satisfiable = [
                        _t for _t in transitions if do_z3_truth_check(_t.guard.smt, _vars)
                    ]

                    # Find the transitions that remain.
                    solved_transitions = trivially_satisfiable + trivially_unsatisfiable
                    remaining_transitions = [_t for _t in transitions if _t not in solved_transitions]

                    # Create the truth matrices for the AND, XOR and implication operators.
                    truth_matrices = calculate_truth_matrices(_vars, remaining_transitions)

                    sub_groupings = []
                    if len(remaining_transitions) > 0:
                        sub_groupings.append(find_deterministic_groups(remaining_transitions, _vars, truth_matrices))

                    choices = trivially_satisfiable + sub_groupings
                    if len(choices) == 0:
                        continue

                    groupings = (Decision.N_DET, choices) if len(choices) > 1 else choices[0]
                    _sm.groupings[_s] = format_decision_group_tree(groupings, trivially_satisfiable)

                    print_determinism_report(_s, _sm, transitions, trivially_satisfiable, trivially_unsatisfiable)

    return model


def print_determinism_report(_s, _sm, transitions, trivially_satisfiable, trivially_unsatisfiable):
    print("#" * 120)
    print("State Machine:", _sm.name)
    print("State:", _s)
    print()
    if len([_t for _t in trivially_satisfiable if _t.guard is not True and _t.guard.smt is not True]) > 0:
        print("WARNING: The following transition guards hold vacuously TRUE:")
        for _t in [_t for _t in trivially_satisfiable if _t.guard is not True and _t.guard.smt is not True]:
            print("\t- %s" % _t)
        print()
    if len([_t for _t in trivially_unsatisfiable]) > 0:
        print("WARNING: The following transition guards are always FALSE:")
        for _t in [_t for _t in trivially_unsatisfiable]:
            print("\t- %s" % _t)
        print()
    print("Transitions:")
    for _t in transitions:
        print("\t- %s" % _t)
    print()
    print("Decisions:")
    print_decision_groups(_sm.groupings[_s])
    print("#" * 120)
    print()


def calculate_truth_matrices(_vars, transitions):
    truth_matrices = {}
    for _o, _m in [("and", False), ("xor", True), ("=>", True)]:
        if _o == "=>":
            # Implication is non-symmetric, so we need to test both directions.
            truth_matrices[_o] = {
                _t: {
                    _t2: do_z3_opr_check(_o, _t.guard.smt, _t2.guard.smt, _vars, _m) for _t2 in transitions
                } for _t in transitions
            }
        else:
            # We don't have to check both directions, since XOR and AND are symmetric.
            truth_matrices[_o] = {}
            for _t in transitions:
                truth_matrices[_o][_t] = {}
                for _t2 in transitions:
                    truth_evaluation = do_z3_opr_check(_o, _t.guard.smt, _t2.guard.smt, _vars, _m)
                    truth_matrices[_o][_t][_t2] = truth_evaluation
                    if _t == _t2:
                        break
                    truth_matrices[_o][_t2][_t] = truth_evaluation
    return truth_matrices


def preprocess(model):
    """"Gather additional data about the model"""
    # Extend and transform the model to one fitting our purpose.
    transform_model(model)

    # Find which transitions can be executed with determinism and add the required information to the model.
    add_determinism_annotations(model)

    return model


add_counter = False
model_folder, model_name = None, None


def slco_to_java(model):
    """The translation function"""
    global add_counter, model_folder, model_name
    out_file = open(os.path.join(model_folder, model.name + ".java"), 'w')

    # write the program
    out_file.write(
        render_model(model, add_counter)
    )
    out_file.close()


def main(_args):
    """The main function"""
    global add_counter, model_folder, model_name

    if len(_args) == 0:
        print("Missing argument: SLCO model")
        sys.exit(1)
    else:
        if any([arg in ["-h", "-help"] for arg in _args]):
            print("Usage: pypy/python3 slco2java")
            print("")
            print("Transform an SLCO 2.0 model to a Java program.")
            print("-c                 produce a transition counter in the code, to make program executions finite")
            sys.exit(0)
        else:
            _i = 0
            while _i < len(_args):
                if _args[_i] == '-c':
                    add_counter = True
                else:
                    model_folder, model_name = os.path.split(_args[_i])
                _i += 1

    # read model
    model = read_SLCO_model(os.path.join(model_folder, model_name))
    # preprocess
    model = preprocess(model)
    # translate
    slco_to_java(model)


if __name__ == '__main__':
    args = []
    for i in range(1, len(sys.argv)):
        args.append(sys.argv[i])
    main(args)
