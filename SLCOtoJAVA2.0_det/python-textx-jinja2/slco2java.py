# SLCO 2.0 to multi-threaded Java transformation, limited to SLCO models consisting of a single object
# import libraries
import os

from determinism_annotations import add_determinism_annotations
from jinja2_filters import *
from model_transformations import transform_model
from slcolib import *

this_folder = dirname(__file__)


def preprocess(model):
    """"Gather additional data about the model"""
    # Extend and transform the model to one fitting our purpose.
    transform_model(model)

    # Find which transitions can be executed with determinism and add the required information to the model.
    add_determinism_annotations(model)

    return model


add_counter = False
model_folder, model_name = None, None


def slco_to_java(model):
    """The translation function"""
    global add_counter, model_folder, model_name
    out_file = open(os.path.join(model_folder, model.name + ".java"), 'w')

    # write the program
    out_file.write(
        render_model(model, add_counter)
    )
    out_file.close()


def main(_args):
    """The main function"""
    global add_counter, model_folder, model_name

    if len(_args) == 0:
        print("Missing argument: SLCO model")
        sys.exit(1)
    else:
        if any([arg in ["-h", "-help"] for arg in _args]):
            print("Usage: pypy/python3 slco2java")
            print("")
            print("Transform an SLCO 2.0 model to a Java program.")
            print("-c                 produce a transition counter in the code, to make program executions finite")
            sys.exit(0)
        else:
            _i = 0
            while _i < len(_args):
                if _args[_i] == '-c':
                    add_counter = True
                else:
                    model_folder, model_name = os.path.split(_args[_i])
                _i += 1

    # read model
    model = read_SLCO_model(os.path.join(model_folder, model_name))
    # preprocess
    model = preprocess(model)
    # translate
    slco_to_java(model)


if __name__ == '__main__':
    args = []
    for i in range(1, len(sys.argv)):
        args.append(sys.argv[i])
    main(args)
