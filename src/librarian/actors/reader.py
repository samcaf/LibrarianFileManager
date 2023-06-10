"""This module defines the Reader class, which is a class
used to read data from files within catalogs.

It can also be used as a base class for other classes which
are designed to read data from files and then _process_ that data
in some way. An example is the Plotter subclass.
"""
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

        raise ModuleNotFoundError("Could not find "
                                  "a valid module for loading the "
                                  f"pickled object. Tried {module} "
                                  f"(given) and {new_modules}.")


# =====================================
# Reader Class
# =====================================
class Reader(Actor):
    """
    A class that reads data from files.

    The Reader class provides methods to read the contents of a file
    as a string or as a list of lines. It also supports loading various
    data formats such as pickled files, NumPy files, and plain text files.

    Parameters
    ----------
    None

    Attributes
    ----------
    None
    """

    def __init__(self):
        pass

    def file_action(self, file_path, **kwargs):
        """
        Perform the file action for the Reader.

        This method handles the file-related actions performed by the Reader
        class. It calls the load_data method with the given file_path.

        Parameters
        ----------
        file_path : str
            The path to the file.

        Returns
        -------
        data : object
            The loaded data from the file.
        """
        return self.load_data(file_path)

    def load_data(self, file_path):
        """
        Load and return data from the given file path.

        Parameters
        ----------
        file_path : str
            The path to the file.

        Returns
        -------
        data : object
            The loaded data.

        Raises
        ------
        ValueError
            If the file extension is not supported.
        """
        extension = "." + file_path.split('.')[-1]
        if extension == '.pkl':
            with open(file_path, 'rb') as file:
                data = BackCompatUnpickler(file).load()
        elif extension in ['.npz', '.npy']:
            data = np.load(file_path, allow_pickle=True, mmap_mode='c')
        else:
            raise ValueError("Extension must be .pkl, .npz, or .npy, "
                             f"not {extension}.")
        return data

    def read_file(self, file_path):
        """
        Read and return the contents of the file as a string.

        Parameters
        ----------
        file_path : str
            The path to the file.

        Returns
        -------
        str
            The contents of the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
        return data

    def read_file_lines(self, file_path):
        """
        Read and return the lines of the file as a list.

        Parameters
        ----------
        file_path : str
            The path to the file.

        Returns
        -------
        list
            A list containing the lines of the file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines
