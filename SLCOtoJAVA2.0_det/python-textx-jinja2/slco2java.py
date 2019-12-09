# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object

# import libraries
from enum import Enum

import jinja2

from jinja2_filters import *
from smt_helper_functions import *
from slcolib import *
import os

this_folder = dirname(__file__)


class TransitDict(dict):
    def __missing__(self, key):
        return key


smt_operator_mappings = TransitDict()
smt_operator_mappings["<>"] = "!="
smt_operator_mappings["!"] = "not"
smt_operator_mappings["&&"] = "and"
smt_operator_mappings["||"] = "or"
smt_operator_mappings["%"] = "mod"


def to_simple_ast(ast):
    """Convert the TextX AST to a simpler and more tidy format"""
    class_name = ast.__class__.__name__
    if class_name in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if ast.right is None:
            return to_simple_ast(ast.left)
        else:
            return smt_operator_mappings[ast.op], to_simple_ast(ast.left), to_simple_ast(ast.right)
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
                return "not", to_simple_ast(ast.ref)
            return to_simple_ast(ast.ref)
        else:
            if ast.sign == "-":
                return "-", 0, to_simple_ast(ast.body)
            if ast.sign == "not":
                return "not", to_simple_ast(ast.body)
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


def transform_statement(_s):
    """Convert the statement to a more workable format"""
    class_name = _s.__class__.__name__

    if class_name == "Composite":
        _s.guard = transform_statement(_s.guard)
        _s.assignments = [transform_statement(_a) for _a in _s.assignments]
    elif class_name == "Expression":
        _s.smt = to_simple_ast(_s)
        return _s

    return _s


def expression_to_string(ast):
    if type(ast) in [str, int, float, bool]:
        return ast
    else:
        operator, ops = ast[0], ast[1:]

        if len(ops) == 2:
            if operator == "var[]":
                return "%s[%s]" % (expression_to_string(ops[0]), expression_to_string(ops[1]))
            else:
                return "(%s %s %s)" % (expression_to_string(ops[0]), operator, expression_to_string(ops[1]))
        else:
            if operator == "var":
                return "%s" % (expression_to_string(ops[0]))
            else:
                return "(%s %s)" % (operator, expression_to_string(ops[0]))


true_primary_properties = {
    "value": True,
    "sign": "",
    "body": None,
    "ref": None
}

true_expression_properties = {
    "left": type("Primary", (object,), true_primary_properties)(),
    "op": "",
    "right": None,
    "smt": True
}
true_expression = type("Expression", (object,), true_expression_properties)()


def transform_transition(_t):
    """Convert the transition to a more workable format"""
    # We determine whether a transition is guarded by looking whether the first statement is an expression.
    first_statement = _t.statements[0]
    class_name = first_statement.__class__.__name__

    transition_guard = None
    if class_name == "Composite":
        transition_guard = transform_statement(first_statement.guard)
    elif class_name == "Expression":
        transition_guard = transform_statement(first_statement)

    _t.source = _t.source.name
    _t.target = _t.target.name
    _t.priority = _t.priority
    _t.guard = true_expression if transition_guard is None else transition_guard

    if transition_guard is None:
        _t.statements = [transform_statement(_s) for _s in _t.statements]
    else:
        _t.statements = [transform_statement(_s) for _s in _t.statements]
        if class_name == "Expression":
            _t.statements = _t.statements[1:]

    type(_t).__repr__ = lambda self: "%s->%s[%s]" % (
        self.source, self.target, expression_to_string(self.guard.smt)
    )
    return _t


# noinspection SpellCheckingInspection
def transform_state_machine(_sm):
    """Convert the state machine to a more workable format"""
    _sm.initialstate = _sm.initialstate.name
    _sm.states = [_s.name for _s in _sm.states]
    _sm.name_to_variable = {_v.name: _v for _v in _sm.variables}
    _sm.transitions.sort(key=lambda x: (x.source.name, x.target.name))
    for _t in _sm.transitions:
        transform_transition(_t)

    _sm.adjacency_list = {
        _s: [
            _t for _t in _sm.transitions if _t.source == _s
        ] for _s in _sm.states
    }


def transform_model(_ast):
    """Transform the model such that it provides all the data required for the code conversion"""
    for _c in _ast.classes:
        _c.name_to_variable = {_v.name: _v for _v in _c.variables}

        for _sm in _c.statemachines:
            transform_state_machine(_sm)

    return _ast


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


def slco_to_java(model_folder, model, add_counter):
    """The translation function"""
    out_file = open(os.path.join(model_folder, model.name + ".java"), 'w')

    # Initialize the template engine.
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(this_folder, '../../jinja2_templates')),
        trim_blocks=True,
        lstrip_blocks=True,
        extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.do', ]
    )

    # Register the filters
    jinja_env.filters['get_java_type'] = get_java_type
    jinja_env.filters['get_default_variable_value'] = get_default_variable_value
    jinja_env.filters['comma_separated_list'] = comma_separated_list
    jinja_env.filters['get_classes'] = get_classes
    jinja_env.filters['get_choice_structure'] = get_choice_structure
    jinja_env.filters['to_java_statement'] = to_java_statement
    jinja_env.filters['get_instruction'] = get_instruction
    jinja_env.filters['get_guard_statement'] = get_guard_statement

    # load the Java template
    template = jinja_env.get_template('java_determinism.jinja2template')

    # write the program
    out_file.write(
        template.render(
            model=model,
            add_counter=add_counter
        )
    )
    out_file.close()


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

    assert model_folder is not None
    assert model_name is not None

    # read model
    model = read_SLCO_model(model_name)
    # preprocess
    model = preprocess(model)
    # translate
    slco_to_java(model_folder, model, add_counter)


if __name__ == '__main__':
    args = []
    for i in range(1, len(sys.argv)):
        args.append(sys.argv[i])
    main(args)
