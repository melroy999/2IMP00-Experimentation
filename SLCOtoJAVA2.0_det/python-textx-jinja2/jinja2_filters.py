import jinja2

from jinja2_view_models import get_decision_block_tree

vercors_verif = False


class TransitDict(dict):
    """A dictionary that returns the key upon query if the key is not present within the dictionary"""
    def __missing__(self, key):
        return key


java_operator_mappings = TransitDict()
java_operator_mappings["<>"] = "!="
java_operator_mappings["="] = "=="
java_operator_mappings["and"] = "&&"
java_operator_mappings["or"] = "||"
java_operator_mappings["not"] = "!"


def get_java_type(model, ignore_size):
    """Maps type names from SLCO to Java"""
    global vercors_verif

    if model.base == "Boolean":
        return "boolean" if model.size < 1 or ignore_size else "boolean[]"
    elif model.base == "Integer" or (model.base == "Byte" and vercors_verif):
        return "int" if model.size < 1 or ignore_size else "int[]"
    elif model.base == "Byte":
        return "byte" if model.size < 1 or ignore_size else "byte[]"


def get_default_variable_value(model):
    """ return default value for given variable """
    if model.defvalue is not None:
        return model.defvalue
    elif len(model.defvalues) > 0:
        return "[%s]" % ", ".join([v for v in model.defvalue])
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
    for _v in sorted(variables, key=lambda v: v.name):
        # Is a value assigned to the variable?
        value = instantiated_variables[_v.name] if _v.name in instantiated_variables else get_default_variable_value(_v)

        if _v.type.size > 1:
            variable_instantiations.append("new %s %s" % (get_java_type(_v.type, False), value))
        elif _v.type.base == "Byte" and not vercors_verif:
            variable_instantiations.append("(byte) %s" % value)
        else:
            variable_instantiations.append("%s" % value)
    return comma_separated_list(variable_instantiations)


def get_instruction(m):
    model_class = m.__class__.__name__

    if model_class == "Assignment":
        var_str = m.left.var.name + ("[" + get_instruction(m.left.index) + "]" if m.left.index is not None else "")
        exp_str = ("(byte) (%s)" if m.left.var.type.base == "Byte" else "%s") % get_instruction(m.right)
        return "%s = %s" % (var_str, exp_str)
    elif model_class == "Composite":
        statement_strings = [get_instruction(m.guard)] if m.guard is not None else []
        statement_strings += [get_instruction(s) for s in m.assignments]
        return "[%s]" % "; ".join(statement_strings)
    elif model_class in ["Expression", "ExprPrec1", "ExprPrec2", "ExprPrec3", "ExprPrec4"]:
        if m.op == "":
            return get_instruction(m.left)
        else:
            return "%s %s %s" % (get_instruction(m.left), java_operator_mappings[m.op], get_instruction(m.right))
    elif model_class == "Primary":
        if m.value is not None:
            exp_str = str(m.value).lower()
        elif m.ref is not None:
            exp_str = m.ref.ref + ("[%s]" % get_instruction(m.ref.index) if m.ref.index is not None else "")
        else:
            exp_str = "(%s)" % get_instruction(m.body)
        return ("!(%s)" if m.sign == "not" else m.sign + "%s") % exp_str
    elif model_class == "VariableRef":
        return m.var.name + ("[%s]" % get_instruction(m.index) if m.index is not None else "")


def get_guard_statement(model):
    if model.__class__.__name__ == "TransitionBlock":
        return get_instruction(model.guard_expression)
    else:
        # Construct a disjunction of statements. Brackets are not needed because of the precedence order.
        # TODO simplify using SMT.
        #   - Remove formulas that are equivalent to an already encountered formula.
        #   - Use implication to check whether one formula is contained in another?
        return " || ".join([get_instruction(_e) for _e in model.encapsulating_guard_expression])


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


def render_state_machine(model, add_counter, _c):
    return java_state_machine_template.render(
        model=model,
        add_counter=add_counter,
        _c=_c
    )


def get_required_locks(model, _sm, _c):
    """Get all the locks needed in the choice structure"""
    model_class = model.__class__.__name__

    if model_class == "Transition":
        # Check if the guard is part of a composite.
        pass
    else:
        # The decision is either deterministic or non-deterministic.
        choice_type, choices = model

        if choice_type.value == 0:
            # Deterministic choice.
            pass
        else:
            # Non-deterministic choice.
            pass

    pass


def construct_decision_code(model, _sm, requires_lock=True, include_guard=True):
    model_class = model.__class__.__name__
    if model_class == "TransitionBlock":
        if not model.starts_with_composite:
            composite_assignments = None
            statements = [construct_decision_code(_s, _sm) for _s in model.statements]
        else:
            composite_assignments = [construct_decision_code(_s, _sm, False) for _s in model.statements[0].assignments]
            statements = [construct_decision_code(_s, _sm) for _s in model.statements[1:]]

        return java_transition_template.render(
            starts_with_composite=model.starts_with_composite,
            statements=statements,
            target=model.target,
            state_machine_name=_sm.name,
            composite_assignments=composite_assignments,
            release_locks=model.release_locks,
            _c=_sm.parent_class
        )
    elif model_class == "Composite":
        guard = get_instruction(model.guard) if not model.guard.is_trivially_satisfiable and include_guard else None
        assignments = [get_instruction(_a) for _a in model.assignments]

        # TODO finish the composite.
        return java_composite_template.render(
            guard=guard,
            assignments=assignments,
            requires_lock=requires_lock,
            include_guard=include_guard,
            _c=_sm.parent_class
        )
    elif model_class == "Assignment":
        return java_assignment_template.render(
            requires_lock=requires_lock,
            locks=model.lock_variables if requires_lock else None,
            assignment=model,
            _c=_sm.parent_class
        )
    elif model_class == "Expression":
        return java_expression_template.render(
            locks=model.lock_variables,
            expression=model,
            _c=_sm.parent_class
        )
    elif model_class == "NonDeterministicBlock":
        choices = [construct_decision_code(choice, _sm) for choice in model.choice_blocks]
        return java_non_deterministic_case_distinction_template.render(
            release_locks=model.release_locks,
            choices=choices,
            _c=_sm.parent_class
        )
    elif model_class == "DeterministicIfThenElseBlock":
        choices = [construct_decision_code(choice, _sm) for choice in model.choice_blocks]
        choice_expressions = [get_guard_statement(choice) for choice in model.choice_blocks]
        return java_if_then_else_template.render(
            acquire_locks=model.acquire_locks,
            release_locks=model.release_locks,
            choice_expressions=choice_expressions,
            choices=choices,
            _c=_sm.parent_class
        )
    elif model_class == "DeterministicCaseDistinctionBlock":
        return ""


def get_decision_structure(model, _sm):
    """Construct the decision code and the execution of the transitions"""
    view_model = get_decision_block_tree(model)
    return construct_decision_code(view_model, _sm)


def to_comma_separated_lock_name_list(model):
    return ", ".join([v[0] + ("" if v[1] is None else "[%s]" % v[1]) for v in sorted(model)])


def to_comma_separated_lock_id_list(model, _c):
    lock_ids = []
    for v in sorted(model):
        base = _c.name_to_variable[v[0]].lock_id
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