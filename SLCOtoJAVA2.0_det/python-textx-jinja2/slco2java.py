# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object

# import libraries
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
        "statements": [transform_statement(_s) for _s in _t.statements]
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


def solve_determinism(model):
    """Observe the transitions in the model and determine which can be done deterministically"""
    for _c in model.classes:
        for _sm in _c.statemachines:
            for _s, transitions in _sm.transitions.items():
                _vars = {**_c.variables, **_sm.variables}

                # Compare each transition to the other.
                start = timer()
                s = z3.Solver()
                has_overlap = {
                    _t: {
                        _t2: do_z3_and_check(s, _t.guard, _t2.guard, _vars) for _t2 in transitions
                    } for _t in transitions
                }
                end = timer()
                print(end - start)

    return model


def preprocess(model):
    """"Gather additional data about the model"""
    model = create_shallow_ast_copy(model)

    # Extend and transform the model to one fitting our purpose.
    transform_model(model)

    solve_determinism(model)

    # for _c in model.classes:
    #     for _sm in _c.statemachines:
    #         for _s, transitions in _sm.transitions.items():
    #             for _t in transitions:
    #                 if _t.guard is not None:
    #                     print(to_z3_format(_t.guard, {**_c.variables, **_sm.variables}))

    # meta_data = construct_model_summary(model)

    # print(meta_data)

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
