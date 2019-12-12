import jinja2


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


def to_java_statement(model, add_counter):
    """Translate the SLCO statement to Java code"""
    model_class = model.__class__.__name__

    if model_class == "Assignment":
        return "%s;" % get_instruction(model)
    elif model_class == "Expression":
        return "if(!(%s)) return false;" % get_instruction(model)
    elif model_class == "Composite":
        return composite_statement_template.render(
            model=model
        )
    else:
        return ""


def get_choice_structure(model, add_counter, sm):
    if model.__class__.__name__ == "Transition":
        return transition_template.render(
            model=model,
            add_counter=add_counter,
            sm=sm
        )
    else:
        choice_type, choices = model

        if choice_type.value == 1:
            return non_deterministic_choice_template.render(
                model=choices,
                add_counter=add_counter,
                sm=sm
            )
        else:
            return deterministic_choice_template.render(
                model=choices,
                add_counter=add_counter,
                sm=sm
            )


def get_guard_statement(model):
    if model.__class__.__name__ == "Transition":
        return get_instruction(model.guard)
    else:
        # Construct a disjunction of statements. Brackets are not needed because of the precedence order.
        # TODO simplify using SMT.
        #   - Remove formulas that are equivalent to an already encountered formula.
        #   - Use implication to check whether one formula is contained in another?
        return " || ".join({"%s" % get_guard_statement(s) for s in model[1]})


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


def render_state_machine(model, add_counter, parent_class):
    return java_state_machine_template.render(
        model=model,
        add_counter=add_counter,
        parent_class=parent_class
    )


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
env.filters['get_choice_structure'] = get_choice_structure
env.filters['to_java_statement'] = to_java_statement
env.filters['get_instruction'] = get_instruction
env.filters['get_guard_statement'] = get_guard_statement
env.filters['get_variable_list'] = get_variable_list
env.filters['get_variable_instantiation_list'] = get_variable_instantiation_list


# load the Java templates
java_model_template = env.get_template('component_templates/java_model_template.jinja2template')
java_class_template = env.get_template('component_templates/java_class_template.jinja2template')
java_state_machine_template = env.get_template('component_templates/java_state_machine_template.jinja2template')

deterministic_choice_template = env.get_template('java_deterministic_choice.jinja2template')
non_deterministic_choice_template = env.get_template('java_non_deterministic_choice.jinja2template')
transition_template = env.get_template('java_transition.jinja2template')
composite_statement_template = env.get_template('java_composite_statement.jinja2template')