import math
import re

# Regex strings used to parse leaves in the tree.
integer_regex = re.compile(r"^(-?\d+)$")
float_regex = re.compile(r"^(-?\d+.\d+)$")
boolean_regex = re.compile(r"^(true|false)$")
variable_regex = re.compile(r"^([a-zA-Z][a-zA-Z0-9]*)$")


# Get the parse tree of the given expression.
def expression_parser(exp):
    # Strip superfluous whitespaces.
    exp = exp.strip()

    # First check if we have a simple format (leaves) with regular expressions.
    if re.match(integer_regex, exp):
        return "int", int(exp)
    if re.match(float_regex, exp):
        return "float", float(exp)
    if re.match(boolean_regex, exp):
        return "bool", exp == "true"
    if re.match(variable_regex, exp):
        return "var", exp

    # Count the brackets to find the highest priority operator.
    open_brackets = 0

    # The list of defined operators, sorted on importance.
    operators = ["&&", "||", "==", "!=", ">=", "<=", ">", "<", "+", "-", "*", "/", "!"]
    operator_matches = {}

    # Iterate over the string and determine which operator is at the root of the tree.
    for i, c in enumerate(exp):
        if open_brackets == 0:
            # Check whether we have found an operator.
            if i + 1 < len(exp) and c + exp[i + 1] in operators:
                # We found a two symbol operator.
                operator_matches[c + exp[i + 1]] = i
            elif c in operators:
                # We found a single symbol operator.
                operator_matches[c] = i

        # Handle brackets.
        if c == "(":
            open_brackets += 1
        elif c == ")":
            open_brackets -= 1

    # Find the highest priority operator.
    for operator in operators:
        if operator in operator_matches:
            # Get the index.
            i = operator_matches[operator]

            # Parse recursively based on the chosen operator.
            if operator == "!":
                # Unary operator.
                return operator, expression_parser(exp[i+1:])
            else:
                # Binary operator.
                return operator, expression_parser(exp[:i]), expression_parser(exp[i+len(operator):])

    # If no matches have been found, we have superfluous brackets.
    return expression_parser(exp[1:-1])


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

generate_sweep_events(transitions[-1:])
