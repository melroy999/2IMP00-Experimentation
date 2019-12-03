# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object
import os
import json
from slcolib import *


# import libraries
this_folder = dirname(__file__)


def to_simple_ast(ast, variables):
    """Convert the xtext AST to a simpler and more tidy format"""
    class_name = ast.__class__.__name__
    if class_name == "Assignment":
        return ":=", to_simple_ast(ast.left, variables), to_simple_ast(ast.right, variables)
    elif class_name in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if ast.right is None:
            return to_simple_ast(ast.left, variables)
        else:
            return ast.op, to_simple_ast(ast.left, variables), to_simple_ast(ast.right, variables)
    elif class_name == "Primary":
        if ast.value is not None:
            return ast.value
        elif ast.ref is not None:
            return to_simple_ast(ast.ref, variables)
        else:
            return to_simple_ast(ast.body, variables)
    elif class_name == "ExpressionRef":
        # Find the variable that is being referred to.
        variable_type = next((_v.type.base for _v in variables if _v.name == ast.ref), None)
        if variable_type is None:
            raise Exception("Variable %s is undefined in the scope of the class/state machine." % ast.ref)

        if ast.index is None:
            return variable_type, ast.ref
        else:
            return variable_type + "[]", ast.ref, to_simple_ast(ast.index, variables)
    elif class_name == "VariableRef":
        if ast.index is None:
            return ast.var.type.base, ast.var.name
        else:
            return ast.var.type.base + "[]", ast.var.name, to_simple_ast(ast.index, variables)
    else:
        raise Exception("NYI")


def get_statement_dict(model, variables):
    class_name = model.__class__.__name__

    statement_dict = {
        "type": class_name
    }

    if class_name == "Composite":
        statement_dict["guard"] = get_statement_dict(model.guard, variables) if model.guard is not None else None
        statement_dict["assignments"] = [get_statement_dict(_s, variables) for _s in model.assignments]
    else:
        statement_dict["ast"] = to_simple_ast(model, variables)

    return statement_dict


def get_transition_dict(model, variables):
    """Construct a dictionary for the transitions, grouped by source node"""
    model.sort(key=lambda v: (v.source.name, v.target.name))

    transition_dict = {}
    for _t in model:
        source = _t.source.name
        target = _t.target.name
        if source not in transition_dict:
            transition_dict[source] = []
        transition_data = {
            "source": source,
            "target": target,
            "statements": [get_statement_dict(_s, variables) for _s in _t.statements]
        }
        transition_dict[source].append(transition_data)

    return transition_dict


def correct_missing_variables(ast, variables):
    return 0


def construct_model_summary(model):
    meta_data = {}

    # Construct the dictionary acting as the AST.
    for _class in model.classes:
        meta_data[_class.name] = {
            "variables": {
                _v.name: (_v.name, _v.type.base, _v.type.size) for _v in _class.variables
            },
            "state_machines": {
                _sm.name: {
                    "variables": {
                        _v.name: (_v.name, _v.type.base, _v.type.size) for _v in _sm.variables
                    },
                    "states": [
                        _v.name for _v in _sm.states
                    ],
                    "initial_state": _sm.initialstate.name,
                    "transitions": get_transition_dict(_sm.transitions, _class.variables + _sm.variables)
                } for _sm in _class.statemachines
            }
        }

    return meta_data


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


def preprocess(model):
    """"Gather additional data about the model"""
    model = create_shallow_ast_copy(model)

    meta_data = construct_model_summary(model)

    print(meta_data)

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
