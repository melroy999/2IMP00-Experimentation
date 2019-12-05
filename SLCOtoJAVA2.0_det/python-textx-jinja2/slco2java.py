# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object

# import libraries
from enum import Enum

from slco_smt_lib import *
from slcolib import *
import os
from timeit import default_timer as timer

this_folder = dirname(__file__)


def to_simple_ast(ast):
    """Convert the xtext AST to a simpler and more tidy format"""
    class_name = ast.__class__.__name__
    if class_name == "Assignment":
        return ":=", to_simple_ast(ast.left), to_simple_ast(ast.right)
    elif class_name in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if ast.right is None:
            return to_simple_ast(ast.left)
        else:
            return ast.op, to_simple_ast(ast.left), to_simple_ast(ast.right)
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
                return "!", to_simple_ast(ast.ref)
            return to_simple_ast(ast.ref)
        else:
            if ast.sign == "-":
                return "-", 0, to_simple_ast(ast.body)
            if ast.sign == "not":
                return "!", to_simple_ast(ast.body)
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


def create_shallow_ast_copy(model):
    """Only gather the data that we are interested in from the textX AST"""
    if model is None:
        return None

    if type(model) in (str, int, float, bool):
        return model

    properties = {}
    for key in dir(model):
        if (not key.startswith("_")) and (not callable(getattr(model, key))) and (key not in ["parent"]):
            attr_value = getattr(model, key)

            if type(attr_value) is list:
                properties[key] = [create_shallow_ast_copy(v) for v in attr_value]
            else:
                properties[key] = create_shallow_ast_copy(attr_value)

    return type(model.__class__.__name__, (), properties)()


def transform_statement(_s):
    """Convert the statement to a more workable format"""
    class_name = _s.__class__.__name__

    if class_name == "Composite":
        _s.guard = to_simple_ast(_s.guard)
        _s.assignments = [transform_statement(_a) for _a in _s.assignments]
    elif class_name in ["Expression", "Assignment"]:
        return to_simple_ast(_s)

    return _s


def transform_transition(_t):
    """Convert the transition to a more workable format"""
    # We determine whether a transition is guarded by looking whether the first statement is an expression.
    first_statement = _t.statements[0]
    class_name = first_statement.__class__.__name__

    transition_guard = None
    if class_name == "Composite":
        transition_guard = to_simple_ast(first_statement.guard)
    elif class_name == "Expression":
        transition_guard = to_simple_ast(first_statement)

    # Create a mutable copy.
    properties = {
        "source": _t.source.name,
        "target": _t.target.name,
        "priority": _t.priority,
        "guard": True if transition_guard is None else transition_guard,
        "statements": [transform_statement(_s) for _s in _t.statements],
        "__repr__": lambda self: "%s->%s[%s]" % (self.source, self.target, str(self.guard))
    }

    return type(_t.__class__.__name__, (), properties)()


# noinspection SpellCheckingInspection
def transform_state_machine(_sm):
    """Convert the state machine to a more workable format"""
    _sm.initialstate = _sm.initialstate.name
    _sm.states = [_s.name for _s in _sm.states]
    _sm.variables = {_v.name: _v for _v in _sm.variables}
    _sm.transitions.sort(key=lambda x: (x.source.name, x.target.name))

    adjacency_list = {
        _s: [
            transform_transition(_t) for _t in _sm.transitions if _t.source.name == _s
        ] for _s in _sm.states
    }
    _sm.transitions = adjacency_list


def transform_model(_ast):
    """Transform the model such that it provides all the data required for the code conversion"""
    for _c in _ast.classes:
        _c.variables = {_v.name: _v for _v in _c.variables}

        for _sm in _c.statemachines:
            transform_state_machine(_sm)

    return _ast


class Decision(Enum):
    DET = 0
    N_DET = 1

    def __repr__(self):
        return self.__str__()


def group_overlapping_transitions(transitions, _vars, truth_matrices, invert=False):
    """Divide the transitions into groups, based on the equality measure"""
    # TODO: The swapping does not guarantee that the result is deterministic.
    # - In this case, inequality is not associative: the remainder may still be deterministic.
    # - The important question is, can this case realistically occur, or is it filtered out by the previous method?
    # - x[0] = 0, x[0] = 1, x[0] = 0 is such a case.
    if len(transitions) == 1:
        return transitions

    # Transitions are in the same group if they have an equality relation with one another.
    groupings = []

    processed_transitions = set()
    queue = set()
    for _t in transitions:
        if _t not in processed_transitions:
            # Find all transitions that have an equality relation with this _t.
            queue.update([_t2 for _t2 in transitions if truth_matrices["and"][_t][_t2] != invert])

            current_group_transitions = []

            while len(queue) > 0:
                _t2 = queue.pop()

                if _t2 not in processed_transitions:
                    # Add the transition to the current group.
                    current_group_transitions += [_t2]

                    # Find all transitions that are related to _t.
                    queue.update([_t3 for _t3 in transitions if truth_matrices["and"][_t2][_t3] != invert])

                    # We do not want to visit the queue head again.
                    processed_transitions.add(_t2)

            # TODO change recursive call to find_deterministic_groups of negation is true.
            # Add the group to the list of groupings.
            groupings += [group_overlapping_transitions(current_group_transitions, _vars, truth_matrices, not invert)]
            # if invert:
            #     groupings += [find_deterministic_groups(current_group_transitions, _vars, truth_matrices)]
            # else:

    # TODO: can we split the sub-groupings further?
    # Idea: group by left-hand variable name.
    # Idea: certain transitions in the groupings may be deterministic to one another.
    print(Decision.DET if not invert else Decision.N_DET, groupings)

    return Decision.DET if not invert else Decision.N_DET, groupings


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
        groupings = group_overlapping_transitions(transitions, _vars, truth_matrices)

        # TODO add smart logic to divide the transitions into smaller groups.
        return groupings
    else:
        # Find the transitions that are not invariably active.
        remaining_transitions = [_t for _t in transitions if _t not in invariably_overlapping_transitions]

        # Recursively solve for the non invariably overlapping transitions.
        if len(remaining_transitions) > 0:
            remaining_groupings = [find_deterministic_groups(remaining_transitions, _vars, truth_matrices)]
        else:
            remaining_groupings = []

        # The resulting sub-grouping is to be processed in parallel with the invariably active transitions.
        return Decision.N_DET, invariably_overlapping_transitions + remaining_groupings

        # TODO what do transitions in the invariably_overlapping_transitions list have as a property?
        # - There exists at least one value for which all transitions in the list are simultaneously active.
        # TODO: This case does not necessarily have to be parallel...
        # - x <= 1, x <= 2, x <= 3 are all invariably overlapping. Partial determinism is possible.


def solve_determinism(model):
    """Observe the transitions in the model and determine which can be done deterministically"""
    for _c in model.classes:
        for _sm in _c.statemachines:
            for _s, transitions in _sm.transitions.items():
                _vars = {**_c.variables, **_sm.variables}

                if len(transitions) > 0:
                    # First check if any of the transitions are vacuously true.
                    vacuously_active_transitions = [_t for _t in transitions if do_z3_truth_check(_t.guard, _vars)]
                    remaining_transitions = [_t for _t in transitions if _t not in vacuously_active_transitions]

                    if len([_t for _t in vacuously_active_transitions if _t.guard != True]) > 0:
                        print("WARNING: The following guards hold vacuously true:")
                        for _t in [_t for _t in vacuously_active_transitions if _t.guard != True]:
                            print("\t- %s" % _t)

                    # Create the truth matrices for the AND, XOR and implication operators.
                    truth_matrices = {}
                    for _o, _m in [("and", False), ("xor", True), ("=>", True)]:
                        if _o == "=>":
                            # Implication is non-symmetric, so we need to test both directions.
                            truth_matrices[_o] = {
                                _t: {
                                    _t2: do_z3_opr_check(_o, _t.guard, _t2.guard, _vars, _m) for _t2 in transitions
                                } for _t in transitions
                            }
                        else:
                            # We don't have to check both directions, since XOR and AND are symmetric.
                            truth_matrices[_o] = {}
                            for _t in transitions:
                                truth_matrices[_o][_t] = {}
                                for _t2 in transitions:
                                    truth_evaluation = do_z3_opr_check(_o, _t.guard, _t2.guard, _vars, _m)
                                    truth_matrices[_o][_t][_t2] = truth_evaluation
                                    if _t == _t2:
                                        break
                                    else:
                                        truth_matrices[_o][_t2][_t] = truth_evaluation

                    if len(remaining_transitions) > 0:
                        sub_groupings = [find_deterministic_groups(remaining_transitions, _vars, truth_matrices)]
                    else:
                        sub_groupings = []

                    if len(vacuously_active_transitions) > 0:
                        groupings = Decision.N_DET, vacuously_active_transitions + sub_groupings
                    else:
                        groupings = sub_groupings[0]

                    print(groupings)

    return model


def preprocess(model):
    """"Gather additional data about the model"""
    model = create_shallow_ast_copy(model)

    # Extend and transform the model to one fitting our purpose.
    transform_model(model)

    solve_determinism(model)

    return model


def main(_args):
    """The main function"""
    add_counter = False
    model_folder, model_name = None, None

    if len(_args) == 0:
        print("Missing argument: SLCO model")
        sys.exit(1)
    else:
        if any([arg in ["-h", "-help"] for arg in _args]):
            print("Usage: pypy/python3 slco2java")
            print("")
            print("Transform an SLCO 2.0 model to a Java program.")
            print(
                "-v                                   produce a list of transition functions with Vercors annotations for formal verification")
            print("-l <file>                            provide locking file for smart locking")
            print(
                "-c                                   produce a transition counter in the code, to make program executions finite")
            sys.exit(0)
        else:
            _i = 0
            while _i < len(_args):
                if _args[_i] == '-c':
                    add_counter = True
                else:
                    model_folder, model_name = os.path.split(_args[_i])
                _i += 1

    assert model_folder is not None
    assert model_name is not None

    # read model
    model = read_SLCO_model(model_name)
    # preprocess
    model = preprocess(model)

    print(model)


# translate


if __name__ == '__main__':
    args = []
    for i in range(1, len(sys.argv)):
        args.append(sys.argv[i])
    main(args)
