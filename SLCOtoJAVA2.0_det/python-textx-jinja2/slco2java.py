# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object
import os
import copy
from slcolib import *


# import libraries
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
            return ast.value
        elif ast.ref is not None:
            return to_simple_ast(ast.ref)
        else:
            return to_simple_ast(ast.body)
    elif class_name == "ExpressionRef":
        if ast.index is None:
            return "Var", ast.ref
        else:
            return "Var[]", ast.ref, to_simple_ast(ast.index)
    elif class_name == "VariableRef":
        if ast.index is None:
            return "Var", ast.var.name
        else:
            return "Var[]", ast.var.name, to_simple_ast(ast.index)
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
        "guard": transition_guard,
        "statements": [transform_statement(_s) for _s in _t.statements]
    }

    return type(_t.__class__.__name__, (), properties)()


# noinspection SpellCheckingInspection
def transform_state_machine(_sm):
    """Convert the state machine to a more workable format"""
    _sm.initialstate = _sm.initialstate.name
    _sm.states = [_s.name for _s in _sm.states]
    _sm.variables = {_v.name: _v for _v in _sm.variables}

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


def preprocess(model):
    """"Gather additional data about the model"""
    model = create_shallow_ast_copy(model)

    # Extend and transform the model to one fitting our purpose.
    transform_model(model)

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
            print("-v                                   produce a list of transition functions with Vercors annotations for formal verification")
            print("-l <file>                            provide locking file for smart locking")
            print("-c                                   produce a transition counter in the code, to make program executions finite")
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
