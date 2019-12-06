def get_java_type(s, ignore_size):
    """Maps type names from SLCO to Java"""
    global vercors_verif

    if s.base == 'Boolean':
        return 'boolean' if s.size < 1 or ignore_size else 'boolean[]'
    elif s.base == 'Integer' or (s.base == 'Byte' and vercors_verif):
        return 'int' if s.size < 1 or ignore_size else 'int[]'
    elif s.base == 'Byte':
        return 'byte' if s.size < 1 or ignore_size else 'byte[]'

