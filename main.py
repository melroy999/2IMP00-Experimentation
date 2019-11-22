import math
import re
from jinja2 import Template, Environment, FileSystemLoader

# Regex strings used to parse leaves in the tree.
from queue import PriorityQueue

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


def merge_event_lists_intersection(*args):
    # Merge the two lists, sort and resolve conflicting events.
    input_events = []
    for events in args:
        input_events.extend(events)
    input_events.sort(key=lambda t: (t[0], t[1], get_union_priority(t[2], t[3]), t[4]))
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
                # If the event combined with the last results in an empty range, remove the last event instead.
                if len(events) == 0 or not (value == events[-1][1] and (inclusive == 0 or events[-1][3] == 0)):
                    events.append(statement)
                else:
                    events.pop()

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
            return merge_event_lists_intersection(events_lh, events_rh)
        elif symbol == "||":
            events_lh = generate_expression_sweep_events(name, lh)
            events_rh = generate_expression_sweep_events(name, rh)
            return merge_event_lists_union(events_lh, events_rh)
        else:
            raise Exception("The given expression does not resolve to a boolean value.")


def get_merge_priority(event_id, inclusive):
    if event_id == 0:
        if inclusive == 0:
            return 3
        else:
            return 1
    else:
        if inclusive == 0:
            return 0
        else:
            return 2


def generate_sweep_events(_transitions):
    # Convert all transitions to their parsed counterpart.
    transitions_parsed = [(name, expression_parser(expression)) for name, expression in _transitions]

    # The list of events we have found.
    transition_to_sweep_events = []

    # Iterate over all the transitions and generate events based on the boolean operations.
    print("Sweep event translations:")
    for name, expression in transitions_parsed:
        transition_events = generate_expression_sweep_events(name, expression)
        print(name, expression, transition_events)
        transition_to_sweep_events.extend([transition_events])
    print()

    events = []
    for event_list in transition_to_sweep_events:
        events += event_list

    events.sort(key=lambda t: (t[0], t[1], get_merge_priority(t[2], t[3])))

    return events


def execute_sweep(_transitions):
    # Generate all events needed in the sweep. The events are already ordered through a merging process.
    events = generate_sweep_events(_transitions)

    # We cannot do anything with an empty event list.
    if len(events) == 0:
        return []

    # A set that contains the current state of the playing field.
    sweep_status = {}

    # The segments we were able to identify during the swipe.
    # Segment format: ((start, inclusive), (end, inclusive), {t1, t2, ...})
    segments = []

    # Process the first event separately such that the right values can be set initially.
    var, value, event_id, inclusive, transition = events[0]
    sweep_status[transition] = transition
    last_segment_opener = (value, inclusive)

    # Visit all events and track the active transitions in the given bracket.
    for i, event in enumerate(events):
        # Skip the first iteration.
        if i == 0:
            continue

        var, value, event_id, inclusive, transition = event
        if event_id == 0:
            # Complete the preceding segment, before processing this event.
            # Events might start at the same moment. If so, skip adding.
            segments.append((last_segment_opener, (value, 1 - inclusive), [*sweep_status]))

            # Update the status and find the corresponding next segment opener.
            sweep_status[transition] = transition
            last_segment_opener = (value, inclusive)
        else:
            # Complete the preceding segment, before processing this event.
            # Events might end at the same moment. If the next is the same, skip adding.
            segments.append((last_segment_opener, (value, inclusive), [*sweep_status]))

            # Update the status and find the corresponding next segment opener.
            sweep_status.pop(transition)
            last_segment_opener = (value, 1 - inclusive)

    for segment in segments[:]:
        start, end, t = segment
        # Merge segments that are generated when multiple transitions start or end at the same point.
        # These segments display the behavior (v, 0), (v, 1) or (v, 1), (v, 0).
        # These statements translate to x > v && x <= v or x >= v && x < v, which are both empty ranges.
        if start[0] == end[0] and (start[1] == 0 or end[1] == 0):
            segments.remove(segment)

        # Remove segments with no active transitions.
        elif len(t) == 0:
            segments.remove(segment)

    return segments


def get_decision_tree(segments):
    if len(segments) == 1:
        # Handle the segment as a leaf.
        start, end, active_transitions = segments[0]

        # If start/end is still defined, add a decision.
        if start is not None and end is not None:
            # base the choice on the left side and continue recursively.
            return start, get_decision_tree([(None, end, active_transitions)]), None
        elif start is not None:
            if start == (float('-inf'), 1):
                return active_transitions
            else:
                return (start[0], 1 - start[1]), None, active_transitions
        elif end is not None:
            if end == (float('inf'), 1):
                return active_transitions
            else:
                return end, None, active_transitions
        else:
            return active_transitions
    else:
        # Split into two lists of equal length segments.
        i = len(segments) // 2
        left_segments = segments[:i]
        right_segments = segments[i:]

        # Decide what value to make the split on.
        start_left, end_left, transitions_left = left_segments[-1]
        start_right, end_right, transitions_right = right_segments[0]

        # Check if a void exists between the two segments and adjust the segment start/end points accordingly.
        left_segments[-1] = (start_left, None, transitions_left)
        if end_left[0] == start_right[0]:
            right_segments[0] = (None, end_right, transitions_right)

        # Chose the left splitter and continue recursively.
        return end_left, get_decision_tree(left_segments), get_decision_tree(right_segments)


file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
if_template = env.get_template('java_if.txt')
if_else_template = env.get_template('java_if_else.txt')


def generate_java_code(decision_tree):
    condition, if_body, else_body = decision_tree

    if if_body is not None:
        condition_string = "x" + (" <= " if condition[1] == 1 else " < ") + str(condition[0])
        if isinstance(if_body, list):
            if_body_string = "System.out.println(" + str(if_body) + ")"
        else:
            if_body_string = generate_java_code(if_body)

        if else_body is not None:
            if isinstance(else_body, list):
                else_body_string = "System.out.println(" + str(else_body) + ")"
            else:
                else_body_string = generate_java_code(else_body)

            # if_else body.
            return if_else_template.render(condition=condition_string, if_body=if_body_string, else_body=else_body_string)
        else:
            # if body.
            return if_template.render(condition=condition_string, if_body=if_body_string)
    elif else_body is not None:
        condition_string = "x" + (" >= " if condition[1] == 0 else " > ") + str(condition[0])
        if isinstance(else_body, list):
            if_body_string = "System.out.println(" + str(else_body) + ")"
        else:
            if_body_string = generate_java_code(else_body)

        # if body.
        return if_template.render(condition=condition_string, if_body=if_body_string)

    raise Exception("Supposedly unreachable branch.")


# The transitions available to the state.
transitions = [
    ("t1", "x >= 10"),
    ("t2", "x == 5 || x == 8"),
    ("t3", "x < 5"),
    ("t4", "x >= 7 && x <= 9"),
    ("t5", "x <= 7 && x >= 9"),
    ("t6", "x > 20 || x < 0"),
    ("t7", "x < 20 || x > 0"),
    ("t8", "((x >= 0 && x <= 2) || (x >= 4 && x <= 6)) && ((x >= 1 && x <= 3) || (x >= 5 && x <= 7))")
]
_segments = execute_sweep(transitions)
print("Segments:")
for v in _segments:
    print(v)
print()
print("Decision tree")
print(get_decision_tree(_segments))
print(generate_java_code(get_decision_tree(_segments)))

print()
# The transitions available to the state.
transitions = [
    ("t1", "x == 5 || x == 8"),
    ("t2", "x == 5 || x == 8"),
]

_segments = execute_sweep(transitions)
print("Segments:")
for v in _segments:
    print(v)
print()
print("Decision tree")
print(get_decision_tree(_segments))
print(generate_java_code(get_decision_tree(_segments)))
