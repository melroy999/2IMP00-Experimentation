class SLCOModelVM:
    def __init__(self, actions, channels, classes, name, objects):
        self.actions = actions
        self.channels = channels
        self.classes = classes
        self.name = name
        self.objects = objects


class ClassVM:
    def __init__(self, name, name_to_variable, ports, statemachines, variables):
        self.name = name
        self.name_to_variable = name_to_variable
        self.ports = ports
        self.statemachines = statemachines
        self.variables = variables


class StateMachineVM:
    def __init__(self, groupings, initialstate, name, name_to_variable, states, transitions, variables):
        self.groupings = groupings
        self.initialstate = initialstate
        self.name = name
        self.name_to_variable = name_to_variable
        self.states = states
        self.transitions = transitions
        self.variables = variables


def to_view_model(model):
    class_name = model.__class__.__name__

    if class_name == "SLCOModel":
        actions = model.actions
        channels = model.channels
        classes = [to_view_model(_c) for _c in model.classes]
        name = model.name
        objects = model.objects
        return SLCOModelVM(actions, channels, classes, name, objects)
    elif class_name == "Class":
        name = model.name
        name_to_variable = model.name_to_variable
        ports = model.ports
        statemachines = [to_view_model(_sm) for _sm in model.statemachines]
        variables = model.variables
        return ClassVM(name, name_to_variable, ports, statemachines, variables)
    elif class_name == "StateMachine":
        groupings = model.groupings
        initialstate = model.initialstate
        name = model.name
        name_to_variable = model.name_to_variable
        states = model.states
        transitions = model.transitions
        variables = model.variables
        return StateMachineVM(groupings, initialstate, name, name_to_variable, states, transitions, variables)
    else:
        return model


