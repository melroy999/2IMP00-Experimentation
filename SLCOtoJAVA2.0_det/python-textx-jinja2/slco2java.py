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


def find_deterministic_groups(transitions, _vars):
    """Find groups that are deterministic in regards to one another"""
    # Check whether we have a list of transitions to dissect.
    if len(transitions) <= 1:
        return None if len(transitions) == 0 else (Decision.DET, transitions)

    # Check which transitions have overlapping guards by simply taking the AND between the guards.
    # TODO recalculations are useless, since the values will not change.
    has_overlap = {
        _t: {
            _t2: do_z3_and_check(_t.guard, _t2.guard, _vars) for _t2 in transitions
        } for _t in transitions
    }

    # Do any of the transitions always possibly overlap with the others transitions?
    invariably_overlapping_transitions = [_t for _t in transitions if all(has_overlap[_t].values())]

    # TODO what do transitions in the invariably_overlapping_transitions list have as a property?
    # - There exists at least one value for which all transitions in the list are simultaneously active.

    # If we have several invariably active transitions, but not all transitions are, divide and conquer.
    if len(invariably_overlapping_transitions) == 0:
        # TODO add smart logic to divide the transitions into smaller groups.
        print("No invariably active transitions")
        return Decision.N_DET, transitions
    else:
        # Find the transitions that are not invariably active.
        remaining_transitions = [_t for _t in transitions if _t not in invariably_overlapping_transitions]

        # Recursively solve for the non invariably active transitions.
        sub_groupings = find_deterministic_groups(remaining_transitions, _vars)

        # The resulting sub-grouping is to be processed in parallel with the invariably active transitions.
        return Decision.N_DET, invariably_overlapping_transitions + [] if sub_groupings is None else [sub_groupings]

        # TODO: This case does not necessarily have to be parallel...
        # x <= 1, x <= 2, x <= 3 are all invariably overlapping. Partial determinism is possible.

    # if len(invariably_active_transitions) > 0:
    #     print("[%s] have overlap with all other transitions." % [_t.guard for _t in invariably_active_transitions])


def solve_determinism(model):
    """Observe the transitions in the model and determine which can be done deterministically"""
    for _c in model.classes:
        for _sm in _c.statemachines:
            for _s, transitions in _sm.transitions.items():
                _vars = {**_c.variables, **_sm.variables}

                # Compare each transition to the other.
                if len(transitions) > 0:
                    # First check if any of the transitions are vacuously true.
                    vacuously_active_transitions = [_t for _t in transitions if do_z3_truth_check(_t.guard, _vars)]
                    remaining_transitions = [_t for _t in transitions if _t not in vacuously_active_transitions]
                    sub_groupings = find_deterministic_groups(remaining_transitions, _vars)

                    if len(vacuously_active_transitions) > 0:
                        vacuously_active_transitions += [] if sub_groupings is None else [sub_groupings]
                        groupings = Decision.N_DET, vacuously_active_transitions
                    else:
                        groupings = sub_groupings

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
