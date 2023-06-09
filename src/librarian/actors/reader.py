"""This module defines the Reader class, which is a class
used to read data from files within catalogs.

It can also be used as a base class for other classes which
are designed to read data from files and then _process_ that data
in some way. An example is the Plotter subclass.
"""

import os

# File storage
import dill as pickle
import numpy as np

# The Reader acts on files:
from librarian.actor import Actor


# =====================================
# Backwards Compatible Unpickler
# =====================================
class BackCompatUnpickler(pickle.Unpickler):
    """A custom unpickler that allows for backwards
    compatibility with older versions of the code.
    """
    def find_class(self, module, name):
        # If file structures change, you can use this
        # to define new places for the unpickler to look
        # for the old classes.
        # Otherwise, pickle won't have access to the classes
        # used during the pickling process, and will throw
        # an error.
        new_lib = ''
        new_modules = [new_lib]

        for try_module in [module] + new_modules:
            try:
                return super().find_class(
                        try_module, name)
            except ModuleNotFoundError:
                pass

        raise ModuleNotFoundError("Could not find "\
                "a valid module for loading the "\
                f"pickled object. Tried {module} "\
                f"(given) and {new_modules}.")


# =====================================
# Reader Class
# =====================================
class Reader(Actor):
    """In the Reader class, we have an __init__ method that initializes the reader.

    The read_file method reads the contents of a file and returns it as a string.
    It takes the file path as a parameter and uses the open function to open the
    file in read mode.

    The read_file_lines method reads the contents of a file and returns a list of
    lines. It takes the file path as a parameter and uses the open function to open
    the file in read mode.
    """
    def __init__(self):
        pass


    def file_action(self, file_path, **kwargs):
        """Defining the file action of the Reader to
        load data from files."""
        return self.load_data(file_path)


    def load_data(self, file_path):
        """Loads and returns data associated with the given
        data name and the given parameters.
        """
        # Finding the extension
        extension = "."+file_path.split('.')[-1]

        # Loading the associated data
        if extension == '.pkl':
            with open(file_path, 'rb') as file:
                data = BackCompatUnpickler(file).load()
        elif extension in ['.npz', '.npy']:
            data = np.load(file_path, allow_pickle=True,
                           mmap_mode='c')
        else:
            raise ValueError("Extension must be .pkl, .npz, or .npy, "\
                             +f" {extension}.")

        return data


    # ---------------------------------
    # Other possible actions
    # ---------------------------------
    def read_file(self, file_path):
        """Reads a file associated with the given
        data name and params.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            return data


    def read_file_lines(self, file_path):
        """Reads the lines of a file associated with the given
        data name and params.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return lines
