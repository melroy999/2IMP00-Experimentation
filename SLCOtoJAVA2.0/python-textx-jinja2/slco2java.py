# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object

import sys
import os
from os.path import dirname, join
import jinja2
from textx.metamodel import metamodel_from_file
import re
from copy import copy, deepcopy

# Set of all state names in the model
states = set([])
# number of transitions in the model
nrtrans = 0
# number of elementary global variables in the model
numberofelemvariables = 0
# dictionary providing for each state machine its local variables
smlocalvars = {}
# dictionary providing lock ids (offset) for a given variable
varids = {}
# set of variable names
varnames = set([])
# locking dictionary (provides variables to lock per object)
lockingdict = {}
# should a transition counter be added to the code? (to make program executions finite)
add_counter = False
# produce a list of transition functions for formal verification with Vercors
vercors_verif = False
vercors_vars = {}
add_performance_counter = False

this_folder = dirname(__file__)

# import libraries
sys.path.append(join(this_folder, '../../libraries'))
from slcolib import *
from SCCTarjan import *

this_folder = dirname(__file__)


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def operator(s):
    """Provide characters to display given operator s"""
    if s == '>':
        return '>'
    elif s == '<':
        return '<'
    elif s == '>=':
        return '>='
    elif s == '<=':
        return '<='
    elif s == '=':
        return '=='
    elif s == '!=':
        return '!='
    elif s == 'and':
        return '&&'
    elif s == 'or':
        return '||'
    elif s == '<>':
        return '!='
    else:
        return s


def sign(s):
    if s == 'not':
        return '!'
    else:
        return s


def getinstruction(s):
    """Get the Java instruction for the given statement s"""
    global vercors_verif

    result = ''
    if s.__class__.__name__ == "Assignment":
        result += s.left.var.name
        if s.left.index != None:
            result += "[" + getinstruction(s.left.index) + "]"
        result += " = "
        if s.left.var.type.base == 'Byte' and not vercors_verif:
            result += "(byte) ("
        result += getinstruction(s.right)
        if s.left.var.type.base == 'Byte' and not vercors_verif:
            result += ")"
    elif s.__class__.__name__ == "Composite":
        result += "["
        if s.guard != None:
            result += getinstruction(s.guard)
        if len(s.assignments) > 1:
            result += ";"
        for i in range(0, len(s.assignments)):
            result += " " + getinstruction(s.assignments[i])
            if i < len(s.assignments) - 1:
                result += ";"
        result += "]"
    elif s.__class__.__name__ == "Expression" or s.__class__.__name__ == "ExprPrec4" or s.__class__.__name__ == "ExprPrec3" or s.__class__.__name__ == "ExprPrec2" or s.__class__.__name__ == "ExprPrec1":
        if s.op != '':
            result += getinstruction(s.left) + " " + operator(s.op) + " " + getinstruction(s.right)
        else:
            result += getinstruction(s.left)
    elif s.__class__.__name__ == "Primary":
        result += sign(s.sign)
        if s.sign == "not":
            result += "("
        if s.value != None:
            newvalue = s.value
            result += str(newvalue).lower()
        elif s.ref != None:
            result += s.ref.ref
            if s.ref.index != None:
                result += "[" + getinstruction(s.ref.index) + "]"
        else:
            result += '(' + getinstruction(s.body) + ')'
        if s.sign == "not":
            result += ")"
    elif s.__class__.__name__ == "VariableRef":
        result += s.var.name
        if s.index != None:
            result += "[" + getinstruction(s.index) + "]"
    return result


def getinstruction_old(s, v, vname):
    """Get the Java instruction for the given statement s, with variable v referred to with name vname (for Vercors verification) """
    global vercors_verif

    result = ''
    if s.__class__.__name__ == "Assignment":
        if s.left.var == v:
            result += vname
        else:
            result += s.left.var.name
        if s.left.index != None:
            result += "[" + getinstruction_old(s.left.index, v, vname) + "]"
        result += " = "
        if s.left.var.type.base == 'Byte' and not vercors_verif:
            result += "(byte) ("
        result += getinstruction_old(s.right, v, vname)
        if s.left.var.type.base == 'Byte' and not vercors_verif:
            result += ")"
    elif s.__class__.__name__ == "Composite":
        result += "["
        if s.guard != None:
            result += getinstruction_old(s.guard, v, vname)
        if len(s.assignments) > 1:
            result += ";"
        for i in range(0, len(s.assignments)):
            result += " " + getinstruction_old(s.assignments[i], v, vname)
            if i < len(s.assignments) - 1:
                result += ";"
        result += "]"
    elif s.__class__.__name__ == "Expression" or s.__class__.__name__ == "ExprPrec4" or s.__class__.__name__ == "ExprPrec3" or s.__class__.__name__ == "ExprPrec2" or s.__class__.__name__ == "ExprPrec1":
        if s.op != '':
            result += getinstruction_old(s.left, v, vname) + " " + operator(s.op) + " " + getinstruction_old(s.right, v,
                                                                                                             vname)
        else:
            result += getinstruction_old(s.left, v, vname)
    elif s.__class__.__name__ == "Primary":
        result += sign(s.sign)
        if s.sign == "not":
            result += "("
        if s.value != None:
            newvalue = s.value
            result += str(newvalue).lower()
        elif s.ref != None:
            if s.ref.ref == v.name:
                result += vname
            else:
                result += s.ref.ref
            if s.ref.index != None:
                result += "[" + getinstruction_old(s.ref.index, v, vname) + "]"
        else:
            result += '(' + getinstruction_old(s.body, v, vname) + ')'
        if s.sign == "not":
            result += ")"
    elif s.__class__.__name__ == "VariableRef":
        if s.var == v:
            result += vname
        else:
            result += s.var.name
        if s.index != None:
            result += "[" + getinstruction_old(s.index, v, vname) + "]"
    return result


def javatype(s, ignoresize):
    """Maps type names from SLCO to Java"""
    global vercors_verif

    if s.base == 'Integer':
        if s.size < 1 or ignoresize:
            return 'int'
        else:
            return 'int[]'
    elif s.base == 'Boolean':
        if s.size < 1 or ignoresize:
            return 'boolean'
        else:
            return 'boolean[]'
    elif s.base == 'Byte':
        if s.size < 1 or ignoresize:
            if not vercors_verif:
                return 'byte'
            else:
                return 'int'
        else:
            if not vercors_verif:
                return 'byte[]'
            else:
                return 'int[]'


def javastatement(s, nlocks, indent, nondet, o, locking, vercors_annot):
    """Translates SLCO statement s to Java code. indent indicates how much every line needs to be indented, nlocks indicates how many locks need to be acquired (optional). nondet indicates whether this statement is at the head of a statement block and in a non-deterministic choice; it affects how expressions are translated.
    o is Object owning s. Finally, boolean locking indicates whether locking instructions should be added or not. vercors_annot is a flag indicating whether Vercors annotations should be added for formal verification."""
    global add_counter, vercors_vars

    # obtain vercors vars list, if needed
    if vercors_annot:
        VercorsV = vercors_vars.get(s, [[], []])

    indentspace = ""
    for i in range(0, indent):
        indentspace += " "
    output = ""
    if s.__class__.__name__ == "Assignment":
        if vercors_annot:
            Alist = used_array_indices(s)
            if Alist != []:
                for a, index in Alist:
                    output += "/*@ assume 0 <= " + str(index) + " < " + str(a) + ".length; @*/\n" + indentspace
            vold = vercors_vars.get(s, "")
            if vold != "":
                output += "/*@ " + vold[1] + " = " + s.left.var.name + "; @*/\n" + indentspace
        output += getinstruction(s) + ";"
    elif s.__class__.__name__ == "Expression":
        if not nondet:
            #			if statement_readsfromlocked(s, o):
            # if vercors_annot:
            # 	Adict = used_array_indices(s,{})
            # 	if Adict != {}:
            # 		for a, indices in Adict.items():
            # 			for index in indices:
            # 				output += "/*@ assume 0 <= " + str(index) + " < " + str(a) + ".length; @*/\n" + indentspace
            output += "if(!(" + getinstruction(s) + ")) {"
            if locking and nlocks > 0:
                output += " java_kp.unlock(java_lockIDs, "
                output += str(nlocks)
                output += ");"
            if add_counter:
                output += " java_transcounter++;"
            output += " return false; }"
        # else:
        # 	output += "while(!(" + getinstruction(s) + ") && java_transcounter < COUNTER_BOUND) { java_kp.unlock(java_lockIDs, "
        # 	output += str(nlocks)
        # 	output += "); java_transcounter++; try{ synchronized(SyncObject){SyncObject.wait(1);} } catch (InterruptedException e) { break; } java_kp.lock(java_lockIDs, "
        # 	output += str(nlocks) + ");}"
        else:
            # if vercors_annot:
            # 	Adict = used_array_indices(s,{})
            # 	if Adict != {}:
            # 		for a, indices in Adict.items():
            # 			for index in indices:
            # 				output += "/*@ assume 0 <= " + str(index) + " < " + str(a) + ".length; @*/\n" + indentspace
            output += "if (!(" + getinstruction(s) + ")) {"
            if locking and nlocks > 0:
                output += " java_kp.unlock(java_lockIDs, "
                output += str(nlocks)
                output += ");"
            if add_counter:
                output += " java_transcounter++;"
            output += " return false; }"
    elif s.__class__.__name__ == "Composite":
        if s.guard != None:
            if vercors_annot:
                Alist = used_array_indices(s.guard)
                if Alist != []:
                    for a, index in Alist:
                        output += "/*@ assume 0 <= " + str(index) + " < " + str(a) + ".length; @*/\n" + indentspace
                output += "/*@ " + str(VercorsV[0][0][1]) + " = " + getinstruction(s.guard) + "; @*/\n" + indentspace
            output += javastatement(s.guard, nlocks, indent, nondet, o, locking, False)
            if len(s.assignments) > 0:
                output += "\n" + indentspace
        first = True
        i = 0
        for e in s.assignments:
            if not first:
                output += "\n" + indentspace
            else:
                first = False
            if vercors_annot:
                Alist = used_array_indices(e)
                if Alist != []:
                    for a, index in Alist:
                        output += "/*@ assume 0 <= " + str(index) + " < " + str(a) + ".length; @*/\n" + indentspace
                output += "/*@ "
                j = 1
                if e.left.index != None:
                    output += VercorsV[1][i][1][1] + " = " + getinstruction(e.left.index) + "; "
                    j = 2
                output += VercorsV[1][i][j][1] + " = " + getinstruction(e.right) + "; @*/\n" + indentspace
                i += 1
            output += getinstruction(e) + ";"
    return output


def concat_unique(L1, L2):
    """Concatenate list L2 to L1, but ensure that no duplicate elements are present"""
    L1set = set(L1)
    L = L1
    for e in L2:
        if e not in L1set:
            L.append(e)
    return L


def used_array_indices(s):
    """Return a list of index expressions for each array access in statement s"""
    L = []
    if s.__class__.__name__ == "Assignment":
        if s.left.index != None:
            L = concat_unique(L, used_array_indices(s.left.index))
            L = concat_unique(L, [(s.left.var.name, getinstruction(s.left.index))])
        L = concat_unique(L, used_array_indices(s.right))
    elif s.__class__.__name__ == "Composite":
        if s.guard != None:
            L = concat_unique(L, used_array_indices(s.guard))
        for i in range(0, len(s.assignments)):
            L = concat_unique(L, used_array_indices(s.assignments[i]))
    elif s.__class__.__name__ == "Expression" or s.__class__.__name__ == "ExprPrec4" or s.__class__.__name__ == "ExprPrec3" or s.__class__.__name__ == "ExprPrec2" or s.__class__.__name__ == "ExprPrec1":
        L = concat_unique(L, used_array_indices(s.left))
        if s.op != '':
            L = concat_unique(L, used_array_indices(s.right))
    elif s.__class__.__name__ == "Primary":
        if s.ref != None:
            if s.ref.index != None:
                L = concat_unique(L, used_array_indices(s.ref.index))
                L = concat_unique(L, [(s.ref.ref, getinstruction(s.ref.index))])
        if s.body != None:
            L = concat_unique(L, used_array_indices(s.body))
    elif s.__class__.__name__ == "VariableRef":
        if s.index != None:
            L = concat_unique(L, used_array_indices(s.index))
            L = concat_unique(L, [(s.var.name, getinstruction(s.index))])
    return L


def used_array_indices_for_guard(s):
    """Return a list of index expressions for each array access in statement s as part of a guard evaluation"""
    if s.__class__.__name__ == "Expression":
        return used_array_indices(s)
    # elif s.__class__.__name__ == "Composite":
    # 	if s.guard != None:
    # 		return used_array_indices(s.guard,L)
    # 	else:
    # 		return {}
    else:
        return []


def expression(s, primmap):
    """Maps SLCO expression to mCRL2 expression. Primmap is a dictionary for rewriting primaries."""
    output = ''
    # special case: s is a variableref. In this case, it is the left-hand side of an assignment, and s refers to an array
    if s.__class__.__name__ == "Variable":
        output = primmap.get(s.name, s.name)
    if s.__class__.__name__ == "Expression" or s.__class__.__name__ == "ExprPrec4" or s.__class__.__name__ == "ExprPrec3" or s.__class__.__name__ == "ExprPrec2":
        # if s.op != '':
        #	output = '('
        if s.op != '' and s.op != 'xor':
            output += expression(s.left, primmap) + " " + operator(s.op) + " " + expression(s.right, primmap)
        elif s.op == 'xor':
            output += operator(s.op) + '(' + expression(s.left, primmap) + ', ' + expression(s.right, primmap) + ')'
        else:
            output += expression(s.left, primmap)
    elif s.__class__.__name__ == "ExprPrec1":
        if s.op != '':
            output += operator(s.op) + '(' + expression(s.left, primmap) + ', ' + expression(s.right, primmap) + ')'
        else:
            output += expression(s.left, primmap)
    elif s.__class__.__name__ == "Primary":
        output = operator(s.sign)
        if s.value != None:
            newvalue = s.value
            output += str(newvalue).lower()
        elif s.ref != None:
            # is an index to an array given?
            key = s.ref.ref
            if s.ref.index != None:
                key += "[" + expression(s.ref.index, primmap) + "]"
            output += primmap.get(key, key)
        else:
            output += '(' + expression(s.body, primmap) + ')'
    return output


def statement_varids(s, sm, primmap):
    """Produce for the given statement a list of sorted lock ids to be acquired. sm is statemachine owning s."""
    global varids, smlocalvars
    output = []
    if s.__class__.__name__ == "VariableRef":
        # is the variable not local to state machine?
        if s.var.name not in smlocalvars[sm]:
            if varids.get(s.var.name) != None:
                varid = varids[s.var.name]
                if s.index != None:
                    varid += " + " + expression(s.index, primmap)
                output.append(varid)
        if s.index != None:
            output += statement_varids(s.index, sm, primmap)
    elif s.__class__.__name__ == "Composite":
        # update primmap
        if s.guard != None:
            output += statement_varids(s.guard, sm, primmap)
        for e in s.assignments:
            output += statement_varids(e.left, sm, primmap)
            output += statement_varids(e.right, sm, primmap)
            newright = expression(e.right, primmap)
            varname = e.left.var.name
            if e.left.index != None:
                varname += "[" + expression(e.left.index, primmap) + "]"
            primmap[varname] = "(" + newright + ")"
    elif s.__class__.__name__ == "Assignment":
        output += statement_varids(s.left, sm, primmap)
        output += statement_varids(s.right, sm, primmap)
    elif s.__class__.__name__ == "ActionRef":
        return []
    elif s.__class__.__name__ != "Primary":
        output += statement_varids(s.left, sm, primmap)
        if s.op != '':
            output += statement_varids(s.right, sm, primmap)
    else:
        if s.ref != None:
            # IGNORE STATE MACHINE LOCAL VARS!
            if s.ref.ref not in smlocalvars[sm]:
                if varids.get(s.ref.ref) != None:
                    varid = varids[s.ref.ref]
                    if s.ref.index != None:
                        varid += " + " + expression(s.ref.index, primmap)
                    output.append(varid)
            if s.ref.index != None:
                output += statement_varids(s.ref.index, sm, primmap)
        if s.body != None:
            output += statement_varids(s.body, sm, primmap)
    # remove duplicates
    output = list(set(output))
    # sort output
    sortedoutput = sorted(output)
    return sortedoutput


def statement_write_varobjects(s):
    """Return a list of objects to which the statement is writing"""
    W = set([])
    if s.__class__.__name__ == "Assignment":
        W.add(s.left.var)
    elif s.__class__.__name__ == "Composite":
        for i in range(0, len(s.assignments)):
            W.add(s.assignments[i].left.var)
    return list(W)


def statement_varobjects(s):
    """Return a list of objects from which the statement is reading"""
    return list(set(statement_write_varobjects(s)) | statement_read_varobjects_set(s, s.parent.parent))


def statement_read_varobjects_set(s, sm):
    """Return a set of objects from which the statement is reading. sm is the state machine owning s."""
    R = set([])
    if s.__class__.__name__ == "Assignment":
        if s.left.index != None:
            R |= statement_read_varobjects_set(s.left.index, sm)
        R |= statement_read_varobjects_set(s.right, sm)
    elif s.__class__.__name__ == "Composite":
        if s.guard != None:
            R |= statement_read_varobjects_set(s.guard, sm)
        for i in range(0, len(s.assignments)):
            R |= statement_read_varobjects_set(s.assignments[i], sm)
    elif s.__class__.__name__ == "Expression" or s.__class__.__name__ == "ExprPrec4" or s.__class__.__name__ == "ExprPrec3" or s.__class__.__name__ == "ExprPrec2" or s.__class__.__name__ == "ExprPrec1":
        R |= statement_read_varobjects_set(s.left, sm)
        if s.op != '':
            R |= statement_read_varobjects_set(s.right, sm)
    elif s.__class__.__name__ == "Primary":
        if s.ref != None:
            if s.ref.index != None:
                R |= statement_read_varobjects_set(s.ref.index, sm)
            # obtain suitable object matching name s.ref.ref
            for v1 in sm_variables(sm):
                if v1.name == s.ref.ref:
                    R.add(v1)
                    break
        if s.body != None:
            R |= statement_read_varobjects_set(s.body, sm)
    elif s.__class__.__name__ == "VariableRef":
        if s.index != None:
            R |= statement_read_varobjects_set(s.index, sm)
        R.add(s.var)
    return R


def statement_writestolocked(s, o):
    """Indicate whether the given statement writes to shared variables that require locking. o is owner Object of statement s."""
    global varids, lockingdict
    output = []
    if s.__class__.__name__ == "VariableRef":
        # is the variable not local to state machine?
        if varids.get(s.var.name) != None:
            if s.var.name in set(lockingdict[o.name]):
                return True
            elif s.index != None:
                index = expression(s.index, {})
                varname = s.var.name + index
                if varname in set(lockingdict[o.name]):
                    return True
                elif not RepresentsInt(index):
                    for v in lockingdict[o.name]:
                        if s.var.name == (v.split("("))[0]:
                            return True
                    return False
                else:
                    return False
            else:
                return False
        else:
            return False
    elif s.__class__.__name__ == "Composite":
        for e in s.assignments:
            result = statement_writestolocked(e.left, o)
            if result:
                return result
        return result
    elif s.__class__.__name__ == "Assignment":
        return statement_writestolocked(s.left, o)
    else:
        return False


def statement_readsfromlocked(s, o):
    """Indicate whether the given statement reads for its guard from shared variables that require locking. o is owner Object of statement s."""
    global varids, lockingdict
    output = []
    if s.__class__.__name__ == "VariableRef":
        # is the variable not local to state machine?
        if varids.get(s.var.name) != None:
            if s.var.name in set(lockingdict[o.name]):
                return True
            elif s.index != None:
                index = expression(s.index, {})
                varname = s.var.name + index
                if varname in set(lockingdict[o.name]):
                    return True
                elif not RepresentsInt(index):
                    for v in lockingdict[o.name]:
                        if s.var.name == (v.split("("))[0]:
                            return True
                    return False
                else:
                    return False
            else:
                return False
        else:
            return False
    elif s.__class__.__name__ == "Composite":
        if s.guard != None:
            return statement_readsfromlocked(s.guard, o)
        else:
            return False
    elif s.__class__.__name__ == "Assignment":
        return False
    elif s.__class__.__name__ != "Primary":
        result = statement_readsfromlocked(s.left, o)
        if result:
            return True
        elif s.op != '':
            return statement_readsfromlocked(s.right, o)
    else:
        if s.ref != None:
            # IGNORE STATE MACHINE LOCAL VARS!
            if varids.get(s.ref.ref) != None:
                if s.ref.ref in set(lockingdict[o.name]):
                    return True
                elif s.ref.index != None:
                    index = expression(s.ref.index, {})
                    varname = s.ref.ref + index
                    if varname in set(lockingdict[o.name]):
                        return True
                    elif not RepresentsInt(index):
                        for v in lockingdict[o.name]:
                            if s.ref.ref == (v.split("("))[0]:
                                return True
                        return False
                    else:
                        return False
                else:
                    return False


def getvarids(s, sm):
    return statement_varids(s, sm, {})


def maxnumbervarids(s):
    """For the given state machine s, determine max number of varids required for a statement contained in it"""
    maxnumber = 0
    for tr in s.transitions:
        for st in tr.statements:
            V = statement_varids(st, s, {})
            if len(V) > maxnumber:
                maxnumber = len(V)
    return maxnumber


def variabledefault(s):
    """ return default value for given variable """
    if s.defvalue != None:
        return s.defvalue
    elif s.defvalues != []:
        defv = '['
        first = True
        for v in s.defvalues:
            if not first:
                defv += ','
            else:
                first = False
            defv += v
        defv += ']'
        return defv
    elif s.type.base == 'Integer' or s.type.base == 'Byte':
        if s.type.size < 2:
            return '0'
        else:
            type = '{'
            first = True
            for i in range(0, s.type.size):
                if not first:
                    type += ','
                else:
                    first = False
                type += '0'
            type += '}'
            return type
    elif s.type.base == 'Boolean':
        if s.type.size < 2:
            return 'true'
        else:
            type = '{'
            first = True
            for i in range(0, s.type.size):
                if not first:
                    type += ','
                else:
                    first = False
                type += 'true'
            type += '}'
            return type


def initialvalue(s, o):
    """ return initial value for given global variable in given object o """
    # try to find variable in initial assignments
    value = ''
    values = []
    for vinit in o.assignments:
        if s.name == vinit.left.name:
            if vinit.right != None:
                value = getinstruction(vinit.right)
            else:
                for v in vinit.rights:
                    values.append(str(v).lower())
    if value != '':
        return value
    elif values != []:
        output = '{'
        first = True
        for v in values:
            if not first:
                output += ','
            else:
                first = False
            output += v
        output += "}"
        return output
    elif s.defvalue != None:
        return s.defvalue
    elif s.defvalues != []:
        defv = '{'
        first = True
        for v in s.defvalues:
            if not first:
                defv += ','
            else:
                first = False
            defv += str(v)
        defv += '}'
        return defv
    elif s.type.base == 'Integer' or s.type.base == 'Byte':
        if s.type.size == 0:
            return '0'
        else:
            type = '{'
            first = True
            for i in range(0, s.type.size):
                if not first:
                    type += ','
                else:
                    first = False
                type += '0'
            type += '}'
            return type
    elif s.type.base == 'Boolean':
        if s.type.size == 0:
            return 'true'
        else:
            type = '{'
            first = True
            for i in range(0, s.type.size):
                if not first:
                    type += ','
                else:
                    first = False
                type += 'true'
            type += '}'
            return type


def outgoingtrans(s, t):
    """Return the set of transitions with s as source"""
    tlist = []
    for tr in t:
        if tr.source.name == s.name:
            tlist.append(tr)
    return tlist


def hasoutgoingtrans(s, t):
    """Check whether state s has outgoing transitions in t"""
    for tr in t:
        if tr.source.name == s.name:
            return True
    return False


def hasglobalvariables(m):
    """Check whether model m has global variables"""
    for c in m.classes:
        if len(c.variables) > 0:
            return True
    return False


def sm_variables(sm):
    """Provide list of variables accessible from current state machine sm"""
    Ldict = {}
    for v in sm.parent.variables:
        Ldict[v.name] = v
    for v in sm.variables:
        Ldict[v.name] = v
    return Ldict.values()


def construct_vercors_auxiliary_vars(model):
    """Produce for all statements in model a list of required auxiliary variables for Vercors verification"""
    global varnames, vercors_vars

    vercors_vars = {}
    for c in model.classes:
        for sm in c.statemachines:
            for tr in sm.transitions:
                for s in tr.statements:
                    L = []
                    bcounter = 0
                    icounter = 0
                    bycounter = 0
                    if s.__class__.__name__ == "Composite":
                        if s.guard != None:
                            while "b" + str(bcounter) in varnames:
                                bcounter += 1
                            L.append([("boolean", "b" + str(bcounter))])
                            bcounter += 1
                        else:
                            L.append([])
                        L1 = []
                        for st in s.assignments:
                            L2 = [st.left.var]
                            if st.left.index != None:
                                while "i" + str(icounter) in varnames:
                                    icounter += 1
                                L2.append(("int", "i" + str(icounter)))
                                icounter += 1
                            if st.left.var.type.base == 'Boolean':
                                while "b" + str(bcounter) in varnames:
                                    bcounter += 1
                                L2.append(("boolean", "b" + str(bcounter)))
                                bcounter += 1
                            elif st.left.var.type.base == 'Integer' or st.left.var.type.base == 'Byte':
                                while "i" + str(icounter) in varnames:
                                    icounter += 1
                                L2.append(("int", "i" + str(icounter)))
                                icounter += 1
                            # else:
                            # 	while "by" + str(bycounter) in varnames:
                            # 		bycounter += 1
                            # 	L2.append(("byte", "by" + str(bycounter)))
                            # 	bycounter += 1
                            L1.append(L2)
                        L.append(L1)
                        vercors_vars[s] = L
                    elif s.__class__.__name__ == "Assignment":
                        # for each variable that we access both for reading and writing, create an auxiliary 'old' variable, to refer to the old value before writing
                        R = set(statement_write_varobjects(s)) & statement_read_varobjects_set(s, sm)
                        print(statement_write_varobjects(s))
                        if len(R) > 0:
                            v = s.left.var
                            newvar = v.name + "_old"
                            counter = 0
                            while newvar + str(counter) in varnames:
                                counter += 1
                            if s.left.var.type.base == 'Boolean':
                                vercors_vars[s] = ("boolean", newvar)
                            elif s.left.var.type.base == 'Integer' or s.left.var.type.base == 'Byte':
                                vercors_vars[s] = ("int", newvar)
                        # else:
                        # 	vercors_vars[s] = ("byte", newvar)


def get_vercors_auxiliary_vars(s):
    """Return the auxiliary vars needed by Vercors to verify statement s"""
    global vercors_vars

    V = vercors_vars.get(s)
    if V == None:
        return []
    else:
        if s.__class__.__name__ == "Composite":
            L = deepcopy(V[0])
            for VL in V[1]:
                for i in range(1, len(VL)):
                    L.append(VL[i])
            return L
        elif s.__class__.__name__ == "Assignment":
            return [V]
        else:
            return []


def get_vercors_guard_auxiliary_var(s):
    """Return auxiliary variable needed for guard of given statement s"""
    global vercors_vars

    if s.__class__.__name__ == "Composite":
        V = vercors_vars.get(s)
        if V == None:
            return ""
        elif len(V[0]) == 0:
            return ""
        else:
            return V[0][0][1]
    elif s.__class__.__name__ == "Expression":
        return "(" + getinstruction(s) + ")"
    else:
        return ""


def get_vercors_last_associated_aux_var(s, v):
    """Return last auxiliary variable associated with given statement s and varobject v. if no such variable exists, return instruction for right-hand side of s, which must be an assignment in that case."""
    global vercors_vars

    if s.__class__.__name__ == "Composite":
        L = vercors_vars.get(s, [[], []])
        for V in reversed(L[1]):
            if V[0] == v:
                return V[len(V) - 1][1]
    elif s.__class__.__name__ == "Assignment":
        oldvarname = vercors_vars.get(s, s.left.var.name)
        return getinstruction_old(s.right, s.left.var, oldvarname[1])
    else:
        return ""


def get_vercors_aux_vars_list(s, v):
    """Return all auxiliary variables associated with given statement s and varobject v"""
    global vercors_vars

    L = vercors_vars.get(s, [[], []])
    L1 = []
    for V in reversed(L[1]):
        if V[0] == v:
            L1.append([V[1], V[2]])
    return L1


def preprocess(model):
    """Preprocess the model"""
    global states, numberofelemvariables, smlocalvars, varids, varnames, nrtrans
    # fill set of state names
    states = set([])
    for c in model.classes:
        for sm in c.statemachines:
            for s in sm.states:
                states.add(s.name)
    # fill set of variable names
    varnames = set([])
    for c in model.classes:
        for v in c.variables:
            varnames.add(v.name)
        for sm in c.statemachines:
            for v in sm.variables:
                varnames.add(v.name)
    # compute number of elementary variables
    numberofelemvariables = 0
    for c in model.classes:
        for v in c.variables:
            if v.type.size > 1:
                numberofelemvariables += v.type.size
            else:
                numberofelemvariables += 1
    # build set of state machine local variable names
    smlocalvars = {}
    for c in model.classes:
        for sm in c.statemachines:
            smlocalvars[sm] = set([v.name for v in sm.variables])
    # build dictionary of global variables with ids
    varids = {}
    # first create list of global variables and sort it
    varlist = []
    for c in model.classes:
        for v in c.variables:
            varlist.append(v)
    sortedlist = sorted(varlist, key=lambda v: v.name)
    # create dict
    count = 0
    for v in sortedlist:
        varids[v.name] = str(count)
        if v.type.size > 1:
            count += v.type.size
        else:
            count += 1
    # determine number of transitions in the model
    nrtrans = 0
    for o in model.objects:
        c = o.type
        for sm in c.statemachines:
            nrtrans += len(sm.transitions)
    return model


lockscanner = re.Scanner([
    (r"[A-Za-z0-9]+:", lambda scanner, token: ("OBJECT", token)),
    (r"[A-Za-z0-9]+(\([0-9]+\))?", lambda scanner, token: ("VARIABLE", token)),
    (r"[\s\(\),]+", None),  # None == skip token.
])


def read_locking_file(model, lockingfilename):
    """Read locking file and return dict of vars to lock"""
    global varids
    lockdict = {}
    if lockingfilename != '':
        try:
            inFile = open(lockingfilename, 'r')
        except IOError:
            print("ERROR: locking file does not exist!")
            exit(1);
        inFile.close()
        key = ''
        for line in open(lockingfilename):
            remainder = line
            while remainder != "":
                results, remainder = lockscanner.scan(remainder)
            if results[0][0] == 'OBJECT':
                key = results[0][1][:-1]
                # lock all variables in case we see 'all_objects'
                if key == "all_objects":
                    lockingfilename = '';
                    break
            else:
                varlist = []
                for i in range(0, len(results)):
                    if results[i][0] == 'VARIABLE':
                        varlist.append(results[i][1])
                oldlist = lockdict.get(key, [])
                varlist += oldlist
                lockdict[key] = varlist
    if lockingfilename == '':
        # fill lockdict with all variables in the system
        for o in model.objects:
            varlist = []
            for v in o.type.variables:
                varname = v.name
                if v.type.size > 1:
                    for i in range(0, v.type.size):
                        varlist.append(varname + "(" + str(i) + ")")
                else:
                    varlist.append(varname)
            lockdict[o.name] = varlist
    return lockdict


def get_identifier(t):
    return "from %s to %s {%s}" % (t.source.name, t.target.name, "; ".join(getlabel(s) for s in t.statements))


def slco_to_java(modelfolder, modelname, model, lockingfilename):
    """The translation function"""
    global states, varids, numberofelemvariables, lockingdict, add_counter, vercors_verif
    outFile = open(os.path.join(modelfolder, model.name + ".java"), 'w')

    # Initialize the template engine.
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(join(this_folder, '../../jinja2_templates')),
                                   trim_blocks=True, lstrip_blocks=True,
                                   extensions=['jinja2.ext.loopcontrols', 'jinja2.ext.do', ])

    # Register the filters
    jinja_env.filters['getvarids'] = getvarids
    jinja_env.filters['statement_writestolocked'] = statement_writestolocked
    jinja_env.filters['statement_readsfromlocked'] = statement_readsfromlocked
    jinja_env.filters['maxnumbervarids'] = maxnumbervarids
    jinja_env.filters['getlabel'] = getlabel
    jinja_env.filters['variabledefault'] = variabledefault
    jinja_env.filters['initialvalue'] = initialvalue
    jinja_env.filters['javatype'] = javatype
    jinja_env.filters['outgoingtrans'] = outgoingtrans
    jinja_env.filters['javastatement'] = javastatement
    jinja_env.filters['hasglobalvariables'] = hasglobalvariables
    jinja_env.filters['get_vercors_auxiliary_vars'] = get_vercors_auxiliary_vars
    jinja_env.filters['get_vercors_guard_auxiliary_var'] = get_vercors_guard_auxiliary_var
    jinja_env.filters['get_vercors_last_associated_aux_var'] = get_vercors_last_associated_aux_var
    jinja_env.filters['get_vercors_aux_vars_list'] = get_vercors_aux_vars_list
    jinja_env.filters['sm_variables'] = sm_variables
    jinja_env.filters['statement_write_varobjects'] = statement_write_varobjects
    jinja_env.filters['statement_varobjects'] = statement_varobjects
    jinja_env.filters['used_array_indices_for_guard'] = used_array_indices_for_guard
    jinja_env.filters['get_identifier'] = get_identifier

    # Register the tests
    jinja_env.tests['hasoutgoingtrans'] = hasoutgoingtrans

    if not vercors_verif:
        # prepare lockingdict information for code generator
        # read locking file
        lockingdict = read_locking_file(model, lockingfilename)
        lockids = []
        for o in model.objects:
            locklist = lockingdict.get(o.name, [])
            for v in locklist:
                vsplit = v.split('(')
                vid = int(varids.get(vsplit[0], "0"))
                if len(vsplit) > 1:
                    vx = vsplit[1].rstrip(')')
                    vid = vid + int(vx)
                lockids.append(vid)
        lockids = set(lockids)
        lockneeded = []
        for i in range(0, numberofelemvariables):
            lockneeded.append(i in lockids)

        # load the Java template
        template = jinja_env.get_template('java.jinja2template')
    else:
        # load the Vercors template
        lockneeded = False
        template = jinja_env.get_template('java_vercors.jinja2template')
        # precompute
        construct_vercors_auxiliary_vars(model)
    # write the program
    outFile.write(
        template.render(model=model, states=states, numberofelemvariables=numberofelemvariables, lockneeded=lockneeded,
                        add_counter=add_counter, add_performance_counter=add_performance_counter))
    outFile.close()


def main(args):
    """The main function"""
    global numberofelemvariables, lockingdict, add_counter, vercors_verif, nrtrans, add_performance_counter
    lockingfilename = ''
    if len(args) == 0:
        print("Missing argument: SLCO model")
        sys.exit(1)
    else:
        if args[0] == '-h' or args[0] == '-help':
            print("Usage: pypy/python3 slco2java")
            print("")
            print("Transform an SLCO 2.0 model to a Java program.")
            print("-v                                   produce a list of transition functions with Vercors annotations for formal verification")
            print("-l <file>                            provide locking file for smart locking")
            print("-c                                   produce a transition counter in the code, to make program executions finite")
            print("-p                                   add profiling counters for the transitions and performance")
            sys.exit(0)
        else:
            i = 0
            while i < len(args):
                if args[i] == '-l':
                    i += 1
                    if i >= len(args):
                        print("ERROR: lock file name missing!")
                        exit(1);
                    lockingfilename = args[i]
                elif args[i] == '-c':
                    add_counter = True
                elif args[i] == '-p':
                    add_performance_counter = True
                elif args[i] == '-v':
                    vercors_verif = True
                else:
                    modelfolder, modelname = os.path.split(args[i])
                i += 1

    # read model
    model = read_SLCO_model(os.path.join(modelfolder, modelname))
    # preprocess
    model = preprocess(model)
    # translate
    slco_to_java(modelfolder, modelname, model, lockingfilename)

    for o in model.objects:
        lockedvars = lockingdict.get(o.name, [])
        lockedvars = set(lockedvars)
    print("SLCO model translated to Java")
    print("number of transition methods in program: " + str(nrtrans))
    if not vercors_verif:
        print("Ratio of locked variables/total number: " + str(len(lockedvars)) + "/" + str(numberofelemvariables))


if __name__ == '__main__':
    args = []
    for i in range(1, len(sys.argv)):
        args.append(sys.argv[i])
    main(args)
