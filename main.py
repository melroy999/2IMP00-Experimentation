import math
import re

# Regex strings used to parse leaves in the tree.
integer_regex = re.compile(r"(-?\d+)$")
float_regex = re.compile(r"(-?\d+.\d+)$")
boolean_regex = re.compile(r"(true|false)$")
variable_regex = re.compile(r"([^ ]+)$")

# Simple brackets.
bracket_regex = re.compile(r"\((.+)\)$")

# Regex strings used to parse boolean operators.
not_regex = re.compile(r"!(.+)$")
and_regex = re.compile(r"(.+) && (.+)$")
or_regex = re.compile(r"(.+) \|\| (.+)$")
equal_regex = re.compile(r"(.+) == (.+)$")
not_equal_regex = re.compile(r"(.+) != (.+)$")
gte_regex = re.compile(r"(.+) >= (.+)$")
lte_regex = re.compile(r"(.+) <= (.+)$")
gt_regex = re.compile(r"(.+) > (.+)$")
lt_regex = re.compile(r"(.+) < (.+)$")

# Regex strings used to parse math operators.
plus_regex = re.compile(r"(.+) \+ (.+)$")
minus_regex = re.compile(r"(.+) - (.+)$")
times_regex = re.compile(r"(.+) \* (.+)$")
divide_regex = re.compile(r"(.+) / (.+)$")


# Get the parse tree of the given expression.
def expression_parser(exp):
    # Strip superfluous whitespaces.
    exp = exp.strip()

    # Check for leaves first, since they are the smallest structures.
    if re.match(integer_regex, exp):
        return "int", int(exp)
    if re.match(float_regex, exp):
        return "float", float(exp)
    if re.match(boolean_regex, exp):
        return "bool", exp == "true"
    if re.match(variable_regex, exp):
        return "var", exp

    # Check Boolean operators.
    if re.match(not_regex, exp):
        m = re.match(not_regex, exp)
        return "!", expression_parser(m.group(0))
    if re.match(and_regex, exp):
        lh, rh = re.match(and_regex, exp).groups()
        return "&&", expression_parser(lh), expression_parser(rh)
    if re.match(or_regex, exp):
        lh, rh = re.match(or_regex, exp).groups()
        return "||", expression_parser(lh), expression_parser(rh)
    if re.match(equal_regex, exp):
        lh, rh = re.match(equal_regex, exp).groups()
        return "==", expression_parser(lh), expression_parser(rh)
    if re.match(not_equal_regex, exp):
        lh, rh = re.match(not_equal_regex, exp).groups()
        return "!=", expression_parser(lh), expression_parser(rh)
    if re.match(gte_regex, exp):
        lh, rh = re.match(gte_regex, exp).groups()
        return ">=", expression_parser(lh), expression_parser(rh)
    if re.match(lte_regex, exp):
        lh, rh = re.match(lte_regex, exp).groups()
        return "<=", expression_parser(lh), expression_parser(rh)
    if re.match(gt_regex, exp):
        lh, rh = re.match(gt_regex, exp).groups()
        return ">", expression_parser(lh), expression_parser(rh)
    if re.match(lt_regex, exp):
        lh, rh = re.match(lt_regex, exp).groups()
        return "<", expression_parser(lh), expression_parser(rh)

    # Check math operators.
    if re.match(plus_regex, exp):
        lh, rh = re.match(plus_regex, exp).groups()
        return "+", expression_parser(lh), expression_parser(rh)
    if re.match(minus_regex, exp):
        lh, rh = re.match(minus_regex, exp).groups()
        return "-", expression_parser(lh), expression_parser(rh)
    if re.match(times_regex, exp):
        lh, rh = re.match(times_regex, exp).groups()
        return "*", expression_parser(lh), expression_parser(rh)
    if re.match(divide_regex, exp):
        lh, rh = re.match(divide_regex, exp).groups()
        return "/", expression_parser(lh), expression_parser(rh)

    # Check for superfluous brackets.
    if re.match(bracket_regex, exp):
        m = re.match(bracket_regex, exp)
        return expression_parser(m.group(1))


# Priority table for line segment configurations.
def get_union_priority(event_id, inclusive):
    if event_id == 0:
        if inclusive == 0:
            return 2
        else:
            return 0
    else:
        if inclusive == 0:
            return 1
        else:
            return 3


def event_list_invert(input_events):
    # Start by sorting the events. We assume that no overlapping ranges exist.
    # The union priority ordering does seem to do the trick here.
    input_events.sort(key=lambda t: (t[0], t[1], get_union_priority(t[2], t[3]), t[4]))
    events = []

    # Traverse the list of events from start to end and find open ranges.
    # Essentially, connect end events to start events.
    for statement in input_events:
        var, value, event_id, inclusive, transition = statement
        if not math.isinf(value):
            events.append((var, value, 1 - event_id, 1 - inclusive, transition))

    if len(events) == 0:
        return []

    # Correct the start and end of the event list.
    var, value, event_id, inclusive, transition = events[-1]
    if event_id == 0:
        # Range is not ended. Add ending.
        events.append((var, float('inf'), 1, 1, transition))

    var, value, event_id, inclusive, transition = events[0]
    if event_id == 1:
        # Range is not started. Add start.
        events.insert(0, (var, float('-inf'), 0, 1, transition))

    return events


def merge_event_lists_union(*args):
    # Merge the two lists, sort and remove superfluous events.
    input_events = []
    for events in args:
        input_events.extend(events)
    input_events.sort(key=lambda t: (t[0], t[1], get_union_priority(t[2], t[3]), t[4]))
    events = []

    # Keep track of the number of open ranges and the leading opening statement of the current segment.
    open_ranges = 0
    opening_statement = input_events[0]

    # Iterate over all events.
    # Open new ranges when the event makes open_ranges non-zero.
    # Close the latest range when open_ranges becomes zero.
    for statement in input_events:
        var, value, event_id, inclusive, transition = statement
        if event_id == 0:
            # A new range has been opened.
            if open_ranges == 0:
                opening_statement = statement

            # Increment the counter.
            open_ranges += 1
        else:
            # A range has been closed.
            open_ranges -= 1

            # If we have no more open ranges, we can add statements for a new range.
            if open_ranges == 0:
                events.extend([opening_statement, statement])
    return events


def merge_event_list_intersection(*args):
    # Merge the two lists, sort and resolve conflicting events.
    input_events = []
    for events in args:
        input_events.extend(events)
    # TODO: choose a sorting order that assures correctness.
    input_events.sort()
    events = []

    # Keep track of the number of open ranges and the leading opening statement of the current segment.
    open_ranges = 0

    # We assume that the given event lists are already in the proper format.
    # Thus, we generate intersection ranges when we have two ranges active simultaneously.
    for statement in input_events:
        var, value, event_id, inclusive, transition = statement
        if event_id == 0:
            # A range has been opened.
            open_ranges += 1

            if open_ranges == len(args):
                # We have multiple ranges open simultaneously. Add current point to range.
                events.append(statement)
        else:
            # We are about to close a range.
            if open_ranges == len(args):
                # We have closed a range. Add current point to range.
                events.append(statement)

            # A range has been closed.
            open_ranges -= 1

    return events


def generate_expression_sweep_events(name, expression):
    # Dissect the expression.
    symbol, lh, rh = expression

    if symbol in ["<", "<=", "==", ">=", ">", "!="]:
        if not (lh[0] == "var" and rh[0] in ["int", "float"]):
            raise Exception("Unsupported input.")
        else:
            # (name, value, event_id, inclusiveness, transition_id)
            # event_id = {0: start, 1: end}
            # inclusiveness = {0: {<,>}, 1: {>=,==,<=}}
            # TODO: Determine the correct inclusive values such that merging is done correctly.
            if symbol == "<":
                return [(lh[1], float('-inf'), 0, 1, name), (lh[1], rh[1], 1, 0, name)]
            elif symbol == "<=":
                return [(lh[1], float('-inf'), 0, 1, name), (lh[1], rh[1], 1, 1, name)]
            elif symbol == "==":
                return [(lh[1], rh[1], 0, 1, name), (lh[1], rh[1], 1, 1, name)]
            elif symbol == ">=":
                return [(lh[1], rh[1], 0, 1, name), (lh[1], float('inf'), 1, 1, name)]
            elif symbol == ">":
                return [(lh[1], rh[1], 0, 0, name), (lh[1], float('inf'), 1, 1, name)]
            elif symbol == "!=":
                return [(lh[1], float('-inf'), 1, 0, name), (lh[1], rh[1], 1, 0, name)] \
                       + [(lh[1], rh[1], 0, 0, name), (lh[1], float('inf'), 1, 1, name)]
    else:
        if symbol == "!":
            events = generate_expression_sweep_events(name, lh)
            return event_list_invert(events)
        elif symbol == "&&":
            events_lh = generate_expression_sweep_events(name, lh)
            events_rh = generate_expression_sweep_events(name, rh)
            return merge_event_list_intersection(events_lh, events_rh)
        elif symbol == "||":
            events_lh = generate_expression_sweep_events(name, lh)
            events_rh = generate_expression_sweep_events(name, rh)
            return merge_event_lists_union(events_lh, events_rh)
        else:
            raise Exception("The given expression does not resolve to a boolean value.")


def generate_sweep_events(_transitions):
    # Convert all transitions to their parsed counterpart.
    transitions_parsed = [(name, expression_parser(expression)) for name, expression in _transitions]
    for name, expression in transitions_parsed:
        print(name, expression)

    # The list of events we have found.
    events = []

    # Iterate over all the transitions and generate events based on the boolean operations.
    for name, expression in transitions_parsed:
        print(generate_expression_sweep_events(name, expression))


# The transitions available to the state.
transitions = [
    ("t1", "x >= 10"),
    ("t2", "x == 5"),
    ("t3", "x < 5"),
    ("t4", "(x == 8)"),
    ("t5", "x >= 7 && x <= 9"),
    ("t6", "x <= 7 && x >= 9"),
    ("t7", "x > 20 || x < 0"),
    ("t8", "x < 20 || x > 0"),
    ("t9", "((x >= 0 && x <= 2) || (x >= 4 && x <= 6)) && ((x >= 1 && x <= 3) || (x >= 5 && x <= 7))")
]

generate_sweep_events(transitions)
