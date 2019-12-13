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

        for block in choice_blocks:
            self.target_locks |= block.target_locks

            if block.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(block.guard_expression)
            else:
                self.encapsulating_guard_expression |= block.encapsulating_guard_expression


class DeterministicIfThenElseBlock:
    """A wrapper for a simple deterministic if-then-else block"""
    # Which locks have to be acquired and released?
    acquire_locks = None
    release_locks = None

    def __init__(self, choice_blocks):
        # Define the choice blocks contained by this construct.
        self.choice_blocks = choice_blocks

        # Which locks should be present?
        self.target_locks = set([])

        # What is the encapsulating guard expression?
        self.encapsulating_guard_expression = set([])

        for block in choice_blocks:
            self.target_locks |= block.target_locks

            if block.__class__.__name__ == "TransitionBlock":
                self.encapsulating_guard_expression.add(block.guard_expression)
            else:
                self.encapsulating_guard_expression |= block.encapsulating_guard_expression


class DeterministicCaseDistinctionBlock:
    """A wrapper for a deterministic case distinction block"""
    subject_expression = None
    default_decision_tree = None
    choice_blocks = []

    # Which locks have to be acquired and released?
    acquire_locks = None
    release_locks = None

    # Which locks should be present?
    target_locks = {}

    # What is the encapsulating guard expression?
    encapsulating_guard_expression = {}

    class DeterministicCaseDistinctionBlockChoice:
        """Inner class for case distinction blocks, providing the target expressions"""
        target_expression = None
        decision_tree = None


class TransitionBlock:
    """A wrapper for a transition leaf in the decision tree"""
    # Which locks have to be acquired and released?
    release_locks = None

    def __init__(self, _t):
        self.guard_expression = _t.guard
        self.statements = _t.statements
        self.starts_with_composite = len(_t.statements) > 0 and _t.statements[0].__class__.__name__ == "Composite"
        self.target = _t.target

        # If the guard is trivially satisfiable, no lock needs to be instantiated for the guard.
        if self.guard_expression.is_trivially_satisfiable or self.guard_expression.is_trivially_unsatisfiable:
            self.target_locks = {}
        elif self.starts_with_composite:
            self.target_locks = self.statements[0].lock_variables
        else:
            self.target_locks = self.guard_expression.lock_variables


def construct_decision_block_tree(model):
    if model.__class__.__name__ == "Transition":
        # Create a transition block.
        return TransitionBlock(model)
    else:
        choice_type, choices = model

        if choice_type.value == 1:
            block = NonDeterministicBlock([construct_decision_block_tree(_c) for _c in choices])
            return block
        else:
            block = DeterministicIfThenElseBlock([construct_decision_block_tree(_c) for _c in choices])
            return block


def propagate_acquire_locks(model, acquired_locks):
    model_class = model.__class__.__name__
    if model_class == "TransitionBlock":
        pass
    elif model_class == "DeterministicCaseDistinctionBlock":
        pass
    elif model_class == "DeterministicIfThenElseBlock":
        # Which locks are not acquired yet?
        missing_locks = model.target_locks.difference(acquired_locks)
        if len(missing_locks) > 0:
            model.acquire_locks = missing_locks
            acquired_locks |= missing_locks

        for block in model.choice_blocks:
            propagate_acquire_locks(block, acquired_locks)

        if len(missing_locks) > 0:
            acquired_locks -= missing_locks
    else:
        for block in model.choice_blocks:
            propagate_acquire_locks(block, acquired_locks)


def propagate_release_locks(model, acquired_locks):
    model_class = model.__class__.__name__
    if model_class == "TransitionBlock":
        # Create a copy of the set, since it is mutable.
        model.release_locks = set(acquired_locks)
    elif model_class == "DeterministicCaseDistinctionBlock":
        pass
    else:
        # Which of the acquired locks can be released?
        lock_release_candidates = acquired_locks.difference(model.target_locks)
        if len(lock_release_candidates) > 0:
            model.release_locks = lock_release_candidates
            acquired_locks -= lock_release_candidates

        if model_class == "DeterministicIfThenElseBlock" and model.acquire_locks is not None:
            acquired_locks |= model.acquire_locks

        for block in model.choice_blocks:
            propagate_release_locks(block, acquired_locks)

        if model_class == "DeterministicIfThenElseBlock" and model.acquire_locks is not None:
            acquired_locks -= model.acquire_locks

        if len(lock_release_candidates) > 0:
            acquired_locks |= lock_release_candidates


def get_decision_block_tree(model):
    decision_tree = construct_decision_block_tree(model)

    # Ensure that the acquire lock tags are set correctly.
    propagate_acquire_locks(decision_tree, set([]))
    propagate_release_locks(decision_tree, set([]))

    return decision_tree
