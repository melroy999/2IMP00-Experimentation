import jinja2

from java_instruction_conversion import get_instruction
from jinja2_view_models import get_decision_block_tree
from smt_functions import z3_truth_check


def get_java_type(model, ignore_size):
    """Maps type names from SLCO to Java"""
    if model.base == "Boolean":
        return "boolean" if model.size < 1 or ignore_size else "boolean[]"
    elif model.base == "Integer":
        return "int" if model.size < 1 or ignore_size else "int[]"
    elif model.base == "Byte":
        return "byte" if model.size < 1 or ignore_size else "byte[]"


def get_default_variable_value(model):
    """ return default value for given variable """
    if model.defvalue is not None:
        return model.defvalue
    elif len(model.defvalues) > 0:
        return "[%s]" % ", ".join([v for v in model.defvalues])
    elif model.type.base in ["Integer", "Byte"]:
        return '0' if model.type.size < 1 else "{%s}" % ", ".join(["0" for _ in range(0, model.type.size)])
    elif model.type.base == "Boolean":
        return 'true' if model.type.size < 1 else "{%s}" % ", ".join(["true" for _ in range(0, model.type.size)])


def comma_separated_list(model):
    return ", ".join(model)


def get_variable_list(model):
    variables = ["%s %s" % (get_java_type(_v.type, False), _v.name) for _v in sorted(model, key=lambda v: v.name)]
    return comma_separated_list(variables)


def get_variable_instantiation_list(model, variables):
    instantiated_variables = {
        _v.left.name: _v.right for _v in model
    }

    variable_instantiations = []
    for v in sorted(variables, key=lambda v2: v2.name):
        # Is a value assigned to the variable?
        value = instantiated_variables[v.name] if v.name in instantiated_variables else get_default_variable_value(v)

        if v.type.size > 1:
            variable_instantiations.append("new %s %s" % (get_java_type(v.type, False), value))
        elif v.type.base == "Byte":
            variable_instantiations.append("(byte) %s" % value)
        else:
            variable_instantiations.append("%s" % value)
    return comma_separated_list(variable_instantiations)


def get_guard_statement(model):
    if model.__class__.__name__ == "TransitionBlock":
        return get_instruction(model.guard_expression)
    else:
        # Construct a disjunction of statements. Brackets are not needed because of the precedence order.
        # TODO simplify using SMT.
        #   - Remove formulas that are equivalent to an already encountered formula.
        #   - Use implication to check whether one formula is contained in another?
        return " || ".join([get_instruction(e) for e in model.encapsulating_guard_expression])


def render_model(model, add_counter):
    return java_model_template.render(
        model=model,
        add_counter=add_counter
    )


def render_class(model, add_counter):
    return java_class_template.render(
        model=model,
        add_counter=add_counter
    )


def render_state_machine(model, add_counter, c):
    return java_state_machine_template.render(
        model=model,
        add_counter=add_counter,
        _c=c
    )


def construct_decision_code(model, sm, requires_lock=True, include_guard=True, include_comment=True):
    model_class = model.__class__.__name__
    if model_class == "TransitionBlock":
        if not model.starts_with_composite:
            composite_assignments = None
            statements = [construct_decision_code(s, sm) for s in model.statements]
        else:
            composite_assignments = [construct_decision_code(s, sm, False) for s in model.composite_assignments]
            statements = [construct_decision_code(s, sm) for s in model.statements[1:]]

        return java_transition_template.render(
            starts_with_composite=model.starts_with_composite,
            composite_assignments=composite_assignments,
            statements=statements,
            target=model.target,
            state_machine_name=sm.name,
            release_locks=model.release_locks,
            _c=sm.parent_class,
            always_fails=model.always_fails,
            comment=model.comment if include_comment else None
        )
    elif model_class == "Composite":
        guard = get_instruction(model.guard) if not model.guard.is_trivially_satisfiable and include_guard else None
        assignments = [get_instruction(a) for a in model.assignments]
        return java_composite_template.render(
            guard=guard,
            assignments=assignments,
            lock_variable_phases=model.lock_variable_phases,
            release_locks=model.lock_variables,
            _c=sm.parent_class
        )
    elif model_class == "Assignment":
        return java_assignment_template.render(
            requires_lock=requires_lock,
            lock_variable_phases=model.lock_variable_phases if requires_lock else None,
            release_locks=model.lock_variables if requires_lock else None,
            assignment=model,
            _c=sm.parent_class
        )
    elif model_class == "Expression":
        return java_expression_template.render(
            lock_variable_phases=model.lock_variable_phases,
            release_locks=model.lock_variables,
            expression=model,
            _c=sm.parent_class
        )
    elif model_class == "ActionRef":
        return "// Execute action [%s]\n" % model.act.name
    elif model_class == "NonDeterministicBlock":
        # Several of the choices may have the same conversion string. Filter these out and merge.
        choices = [(
            construct_decision_code(choice, sm),
            choice.comment if choice.__class__.__name__ == "TransitionBlock" else None
        ) for choice in model.choice_blocks]
        choices.sort(key=lambda v: v[0])

        for i in range(0, len(choices) - 1):
            # Check if the next execution code is equivalent to the current one.
            # If so, set the current execution code to empty string, to avoid duplicates.
            # Note that there is a comment that will likely differ--filter the comment out if appropriate.
            current_choice = choices[i][0]
            if choices[i][1] is not None:
                current_choice = current_choice.replace(choices[i][1], "")

            next_choice = choices[i + 1][0]
            if choices[i + 1][1] is not None:
                next_choice = next_choice.replace(choices[i + 1][1], "")

            if current_choice == next_choice:
                # We still want the traceability comment if applicable.
                choices[i] = ("// %s (functional duplicate of case below)" % choices[i][1], choices[i][1])

        # Remove the choice comment from every choice.
        choices = [choice[0] for choice in choices]

        # If only one choice remains, there is no reason to include an entire block.
        if len(choices) == 1:
            return choices[0]

        return java_non_deterministic_case_distinction_template.render(
            release_locks=model.release_locks,
            choices=choices,
            _c=sm.parent_class
        )
    elif model_class == "DeterministicIfThenElseBlock":
        # Order the choices such that the generated code is always the same.
        choices = [
            (
                construct_decision_code(choice, sm, include_comment=False),
                get_guard_statement(choice),
                choice.comment if choice.__class__.__name__ == "TransitionBlock" else None
            ) for choice in model.choice_blocks
        ]
        choices.sort(key=lambda v: v[0])

        # Does the combination of all the guards always evaluate to true?
        else_choice = None
        if len(model.encapsulating_guard_expression) > 1 and len(model.choice_blocks) > 1:
            encapsulating_guard_expression = list(model.encapsulating_guard_expression)
            smt = encapsulating_guard_expression[0].smt
            for expression in encapsulating_guard_expression[1:]:
                smt = ("or", smt, expression.smt)
            variables = {**sm.parent_class.name_to_variable, **sm.name_to_variable}
            if z3_truth_check(smt, variables):
                else_choice = choices[-1]
                choices = choices[:-1]

        return java_if_then_else_template.render(
            lock_variable_phases=model.lock_variable_phases,
            release_locks=model.release_locks,
            target_locks=model.target_locks,
            choices=choices,
            _c=sm.parent_class,
            else_choice=else_choice
        )
    elif model_class == "DeterministicCaseDistinctionBlock":
        # Several of the choices may have the same conversion string. Filter these out and merge.
        choices = [
            (
                target,
                construct_decision_code(choice, sm, include_comment=False),
                choice.comment if choice.__class__.__name__ == "TransitionBlock" else None
            ) for (target, choice) in model.choice_blocks
        ]
        choices.sort(key=lambda v: v[1])

        for i in range(0, len(choices) - 1):
            # Check if the next execution code is equivalent to the current one.
            # If so, set the current execution code to empty string, to avoid duplicates.
            if choices[i][1] == choices[i + 1][1]:
                choices[i] = (choices[i][0], "", "%s (functional duplicate of case below)" % choices[i][2])

        subject_expression = get_instruction(model.subject_expression)
        default_decision_tree = construct_decision_code(model.default_decision_tree, sm)
        return java_case_distinction_template.render(
            lock_variable_phases=model.lock_variable_phases,
            release_locks=model.release_locks,
            target_locks=model.target_locks,
            subject_expression=subject_expression,
            default_decision_tree=default_decision_tree,
            choices=choices,
            _c=sm.parent_class
        )


def get_decision_structure(model, sm):
    """Construct the decision code and the execution of the transitions"""
    view_model = get_decision_block_tree(model, sm.parent_class)
    return construct_decision_code(view_model, sm)


def to_comma_separated_lock_name_list(model):
    return ", ".join([v[0] + ("" if v[1] is None else "[%s]" % v[1]) for v in sorted(model)])


def to_comma_separated_lock_id_list(model, c):
    lock_ids = []
    for v in sorted(model):
        base = c.name_to_variable[v[0]].lock_id
        index = 0 if v[1] is None else v[1]
        try:
            index = int(index)
            lock_ids.append(str(base + index))
        except (ValueError, TypeError):
            if base == 0:
                lock_ids.append(index)
            else:
                lock_ids.append("%s + %s" % (base, index))
    return ", ".join(lock_ids)


# Initialize the template engine.
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('../../jinja2_templates'),
    trim_blocks=True,
    lstrip_blocks=True,
    extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.do', ]
)

# Register the filters
env.filters['render_class'] = render_class
env.filters['render_state_machine'] = render_state_machine

env.filters['get_java_type'] = get_java_type
env.filters['get_default_variable_value'] = get_default_variable_value
env.filters['comma_separated_list'] = comma_separated_list
env.filters['get_instruction'] = get_instruction
env.filters['get_guard_statement'] = get_guard_statement
env.filters['get_variable_list'] = get_variable_list
env.filters['get_decision_structure'] = get_decision_structure
env.filters['get_variable_instantiation_list'] = get_variable_instantiation_list
env.filters['to_comma_separated_lock_name_list'] = to_comma_separated_lock_name_list
env.filters['to_comma_separated_lock_id_list'] = to_comma_separated_lock_id_list


# load the Java templates
java_model_template = env.get_template('component_templates/java_model_template.jinja2template')
java_class_template = env.get_template('component_templates/java_class_template.jinja2template')
java_state_machine_template = env.get_template('component_templates/java_state_machine_template.jinja2template')
java_assignment_template = env.get_template('component_templates/java_assignment_template.jinja2template')
java_expression_template = env.get_template('component_templates/java_expression_template.jinja2template')
java_composite_template = env.get_template('component_templates/java_composite_template.jinja2template')
java_transition_template = env.get_template('component_templates/java_transition_template.jinja2template')

java_if_then_else_template = env.get_template('decision_templates/java_if_then_else_template.jinja2template')
java_case_distinction_template = env.get_template('decision_templates/java_case_distinction_template.jinja2template')
java_non_deterministic_case_distinction_template = env.get_template(
    'decision_templates/java_non_deterministic_case_distinction_template.jinja2template'
)