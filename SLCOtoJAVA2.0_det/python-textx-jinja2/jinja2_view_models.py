from variable_locking import get_locking_phases, correct_dependency_graph, construct_variable_dependency_graph


class NonDeterministicBlock:
    """A wrapper for a non-deterministic choice"""
    # Which locks have to be released?
    release_locks = None

    def __init__(self, choice_blocks):
        # Define the choice blocks contained by this construct.
        self.choice_blocks = choice_blocks

        # Which locks should be present?
        self.target_locks = set([])

        # What is the encapsulating guard expression?
        self.encapsulating_guard_expression = set([])

        # Which statements are used as guards?
        self.encapsulating_guard_statements = set([])

        for block in choice_blocks:
            self.target_locks |= block.target_locks

            if block.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(block.guard_expression)
                self.encapsulating_guard_statements.add(block.guard)
            else:
                self.encapsulating_guard_expression |= block.encapsulating_guard_expression
                self.encapsulating_guard_statements |= block.encapsulating_guard_statements


class DeterministicIfThenElseBlock:
    """A wrapper for a simple deterministic if-then-else block"""
    # Which locks have to be acquired and released?
    acquire_locks = None
    lock_variable_phases = None
    release_locks = None

    def __init__(self, choice_blocks):
        # Define the choice blocks contained by this construct.
        self.choice_blocks = choice_blocks

        # Which locks should be present?
        self.target_locks = set([])

        # What is the encapsulating guard expression?
        self.encapsulating_guard_expression = set([])

        # Which statements are used as guards?
        self.encapsulating_guard_statements = set([])

        for block in choice_blocks:
            self.target_locks |= block.target_locks

            if block.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(block.guard_expression)
                self.encapsulating_guard_statements.add(block.guard)
            else:
                self.encapsulating_guard_expression |= block.encapsulating_guard_expression
                self.encapsulating_guard_statements |= block.encapsulating_guard_statements


class DeterministicCaseDistinctionBlock:
    """A wrapper for a deterministic case distinction block"""
    # Which locks have to be acquired and released?
    acquire_locks = None
    lock_variable_phases = None
    release_locks = None

    def __init__(self, subject_expression, choice_blocks, default_decision_tree):
        # Define the choice blocks contained by this construct.
        self.choice_blocks = choice_blocks
        self.subject_expression = subject_expression
        self.default_decision_tree = default_decision_tree

        # Which locks should be present?
        self.target_locks = set([])

        # What is the encapsulating guard expression?
        self.encapsulating_guard_expression = set([])

        # Which statements are used as guards?
        self.encapsulating_guard_statements = set([])

        for target, block in choice_blocks:
            self.target_locks |= block.target_locks

            if block.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(block.guard_expression)
                self.encapsulating_guard_statements.add(block.guard)
            else:
                self.encapsulating_guard_expression |= block.encapsulating_guard_expression
                self.encapsulating_guard_statements |= block.encapsulating_guard_statements

        if default_decision_tree is not None:
            self.target_locks |= default_decision_tree.target_locks

            if default_decision_tree.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(default_decision_tree.guard_expression)
                self.encapsulating_guard_statements.add(default_decision_tree.guard)
            else:
                self.encapsulating_guard_expression |= default_decision_tree.encapsulating_guard_expression
                self.encapsulating_guard_statements |= default_decision_tree.encapsulating_guard_statements


class TransitionBlock:
    """A wrapper for a transition leaf in the decision tree"""
    # Which locks have to be acquired and released?
    release_locks = None

    def __init__(self, t):
        self.guard = t.guard
        self.guard_expression = t.guard_expression
        self.statements = t.statements
        self.starts_with_composite = t.guard.__class__.__name__ == "Composite"
        self.composite_assignments = t.guard.assignments if self.starts_with_composite else None
        self.target = t.target
        self.always_fails = t.always_fails

        # Which traceability comment would we like to add?
        self.comment = t.comment_string

        # If the guard is trivially satisfiable, no lock needs to be instantiated for the guard.
        # Recall that composites with a true guard will never be a guard of a transition.
        if self.guard_expression.is_trivially_satisfiable or self.guard_expression.is_trivially_unsatisfiable:
            self.target_locks = set([])
        else:
            self.target_locks = t.guard.lock_variables

    def __repr__(self):
        return self.guard_expression.__repr__()


def construct_decision_block_tree(model):
    """Convert the determinism groupings to their associated view models"""
    if model.__class__.__name__ == "Transition":
        # Create a transition block.
        return TransitionBlock(model)
    else:
        choice_type, choices = model

        if choice_type.value == 1:
            return NonDeterministicBlock([construct_decision_block_tree(_c) for _c in choices])
        else:
            # Determine which types of deterministic blocks to use.
            choice_blocks = [construct_decision_block_tree(_c) for _c in choices]

            # Case distinctions require an equality operation, with a constant right hand side.
            case_compatible_choices = {}
            key_to_expression = {}
            for choice in choice_blocks:
                if choice.__class__.__name__ == "TransitionBlock":
                    guard_expression = choice.guard_expression
                elif len(choice.encapsulating_guard_expression) == 1:
                    guard_expression = next(iter(choice.encapsulating_guard_expression))
                else:
                    # The choice cannot be part of a case distinction.
                    continue

                # Check if the choice block's expression has the right format.
                if not guard_expression.is_trivially_satisfiable and not guard_expression.is_trivially_unsatisfiable:
                    operator, arguments = guard_expression.smt[0], guard_expression.smt[1:]
                    if operator == "=" and type(arguments[1]) == int:
                        key_to_expression[arguments[0]] = guard_expression.left.left
                        case_group = case_compatible_choices.get(arguments[0], [])
                        case_group.append((arguments[1], choice))
                        case_compatible_choices[arguments[0]] = case_group

            # We are only interested in case distinctions with three or more values.
            case_compatible_choices = {
                subject: targets for subject, targets in case_compatible_choices.items() if len(targets) > 2
            }

            # Does a clear case distinction exist?
            if len(case_compatible_choices) == 0:
                return DeterministicIfThenElseBlock(choice_blocks)

            # Construct the case blocks.
            processed_choices = set([])
            for subject, targets in case_compatible_choices.items():
                for target, grouping in targets:
                    processed_choices.add(grouping)

            # If we have just one key, all other choices will end up in the default case.
            remaining_blocks = [b for b in choice_blocks if b not in processed_choices]
            if len(case_compatible_choices) == 1:
                for subject, targets in case_compatible_choices.items():
                    return DeterministicCaseDistinctionBlock(
                        key_to_expression[subject],
                        targets,
                        DeterministicIfThenElseBlock(remaining_blocks)
                    )
            else:
                # Otherwise, make a top level if-then-else statement.
                case_distinction_blocks = [
                    DeterministicCaseDistinctionBlock(
                        key_to_expression[subject], targets, None
                    ) for subject, targets in case_compatible_choices.items()
                ]
                return DeterministicIfThenElseBlock(case_distinction_blocks + remaining_blocks)


def propagate_acquire_locks(model, name_to_variable):
    """Propagate the locks to acquire over the choice block view models"""
    model_class = model.__class__.__name__
    if model_class == "NonDeterministicBlock":
        for block in model.choice_blocks:
            propagate_acquire_locks(block, name_to_variable)
    elif model_class != "TransitionBlock":
        # We always acquire the locks at the soonest convenience--further recursion is unnecessary.
        # Make sure that we acquire the locks in the desired phases.
        model.acquire_locks = set(model.target_locks)
        variable_dependency_graph = {}
        for expression in model.encapsulating_guard_statements:
            construct_variable_dependency_graph(expression, variable_dependency_graph, set(name_to_variable.keys()))

        # If a node has a dependency on a higher id node, expand and remove all dependencies of the node.
        correct_dependency_graph(variable_dependency_graph, name_to_variable, None)

        # Break the lock id list into different phases, following the dependency graph.
        model.lock_variable_phases = get_locking_phases(variable_dependency_graph, name_to_variable, model.target_locks)


def propagate_release_locks(model, acquired_locks):
    """Propagate the locks to release over the choice block view models"""
    model_class = model.__class__.__name__
    if model_class == "TransitionBlock":
        # Create a copy of the set, since it is mutable.
        model.release_locks = set(acquired_locks)
    else:
        # Which of the acquired locks can be released?
        lock_release_candidates = acquired_locks.difference(model.target_locks)
        if len(lock_release_candidates) > 0:
            model.release_locks = lock_release_candidates
            acquired_locks -= lock_release_candidates

        if model_class != "NonDeterministicBlock" and model.acquire_locks is not None:
            acquired_locks |= model.acquire_locks

        if model_class == "DeterministicCaseDistinctionBlock":
            for _, block in model.choice_blocks:
                propagate_release_locks(block, acquired_locks)
            if model.default_decision_tree:
                propagate_release_locks(model.default_decision_tree, acquired_locks)
        else:
            for block in model.choice_blocks:
                propagate_release_locks(block, acquired_locks)

        if model_class != "NonDeterministicBlock" and model.acquire_locks is not None:
            acquired_locks -= model.acquire_locks

        if len(lock_release_candidates) > 0:
            acquired_locks |= lock_release_candidates


def get_decision_block_tree(model, class_object):
    """Convert the decision groups to their view model representation with the appropriate data"""
    decision_tree = construct_decision_block_tree(model)

    # Ensure that the acquire lock tags are set correctly.
    propagate_acquire_locks(decision_tree, class_object.name_to_variable)
    propagate_release_locks(decision_tree, set([]))

    return decision_tree
