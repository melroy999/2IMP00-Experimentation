class NonDeterministicBlock:
    """A wrapper for a non-deterministic choice"""
    choice_blocks = []

    # Does the structure have to acquire the locks?
    acquire_locks = False

    # Which locks have to be acquired?
    locks_to_acquire = {}

    # What is the encapsulating guard expression, and does it require one?
    encapsulating_guard_expression = None
    requires_encapsulating_guard_expression = False

    # TODO: If all choices have the same guard expression, no encapsulating guard is needed!


class DeterministicIfThenElseBlock:
    """A wrapper for a simple deterministic if-then-else block"""
    choice_blocks = []

    # Does the structure have to acquire the locks?
    acquire_locks = False

    # Which locks have to be acquired?
    # TODO: A lock needs to be acquired if the block is at the root of the tree.
    locks_to_acquire = {}


class DeterministicCaseDistinctionBlock:
    """A wrapper for a deterministic case distinction block"""
    subject_expression = None
    default_decision_tree = None
    choice_blocks = []

    # Which locks have to be acquired?
    # TODO: A lock needs to be acquired if the block is at the root of the tree.
    locks_to_acquire = {}

    # What is the encapsulating guard expression, and does it require one?
    encapsulating_guard_expression = None
    requires_encapsulating_guard_expression = False
    # TODO: An encapsulating guard expression is needed if the block is part of a deterministic if-then-else block

    class DeterministicCaseDistinctionBlockChoice:
        """Inner class for case distinction blocks, providing the target expressions"""
        target_expression = None
        decision_tree = None


class TransitionBlock:
    """A wrapper for a transition leaf in the decision tree"""
    guard_expression = None
    statements = []
    starts_with_composite = False
    # TODO: Additional locks need to be acquired if the statement starts with a composite.
    #   - Note that a composite with no guard or a trivially satisfiable guard does not have to be preemptively locked!

    # Which locks have to be acquired prior to calling the transition?
    locks_to_acquire = {}

    def __init__(self, _t):
        self.guard_expression = _t.guard
        self.statements = _t.statements
        self.starts_with_composite = len(_t.statements) > 0 and _t.statements[0].__class__.__name__ == "Composite"

        # If the guard is trivially satisfiable, no lock needs to be instantiated for the guard.
        if self.guard_expression.smt is True:
            self.locks_to_acquire = {}
        elif self.starts_with_composite:
            # TODO: if the guard is trivially satisfiable, the associated variables are erroneously still locked.
            self.locks_to_acquire = self.statements[0].lock_variables
        else:
            self.locks_to_acquire = self.guard_expression.lock_variables


def construct_decision_block_tree(model):
    if model.__class__.__name__ == "Transition":
        # Create a transition block.
        return TransitionBlock(model)
    else:
        choice_type, choices = model

        if choice_type.value == 1:
            block = NonDeterministicBlock()
            block.choice_blocks = [construct_decision_block_tree(_c) for _c in choices]
            return block
        else:
            # TODO: Determine whether we can use a case distinction instead of an if-then-else construct.
            transition_choices = [_c for _c in choices if _c.__class__.__name__ == "Transition"]
            block = DeterministicIfThenElseBlock()
            block.choice_blocks = [construct_decision_block_tree(_c) for _c in choices]
            return block
