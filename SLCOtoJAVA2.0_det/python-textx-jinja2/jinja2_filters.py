vercors_verif = False


def get_java_type(s, ignore_size):
    """Maps type names from SLCO to Java"""
    global vercors_verif

    if s.base == "Boolean":
        return "boolean" if s.size < 1 or ignore_size else "boolean[]"
    elif s.base == "Integer" or (s.base == "Byte" and vercors_verif):
        return "int" if s.size < 1 or ignore_size else "int[]"
    elif s.base == "Byte":
        return "byte" if s.size < 1 or ignore_size else "byte[]"


def get_default_variable_value(s):
    """ return default value for given variable """
    if s.defvalue is not None:
        return s.defvalue
    elif len(s.defvalues) > 0:
        return "[%s]" % ", ".join([v for v in s.defvalue])
    elif s.type.base in ["Integer", "Byte"]:
        return '0' if s.type.size < 1 else "{%s}" % ", ".join(["0" for _ in range(0, s.type.size)])
    elif s.type.base == "Boolean":
        return 'true' if s.type.size < 1 else "{%s}" % ", ".join(["true" for _ in range(0, s.type.size)])


def list_states(states):
    return ", ".join([s.name for s in states])


def get_classes(model):
    return model.classes


def get_grouping(sm, state, model, c):
    return sm.groupings[state]
