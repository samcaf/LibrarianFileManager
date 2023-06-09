"""This module defines the Writer class, which is designed to
write data to files and store the filenames in a catalog.
"""

import warnings

# File storage
import dill as pickle
import numpy as np

# The Reader acts on files:
from librarian.actor import Actor


class Writer(Actor):
    """In the Writer class, we have an __init__ method that initializes
    the writer and takes a catalog object as a parameter. This catalog
    object is used to add the file to the associated catalog when writing
    a file.

    The write_file method writes the provided data to a file. It takes the
    file path and the data as parameters and uses the open function to open
    the file in write mode. After writing the data to the file, it adds the
    file path to the associated catalog using the add_file method.

    The write_file_lines method writes the provided lines to a file.
    It takes the file path and a list of lines as parameters and uses
    the open function to open the file in write mode. After writing the
    lines to the file, it adds the file path to the associated catalog
    using the add_file method.

    Note that the Writer class assumes that the associated catalog object
    passed during initialization has an add_file method to add the file
    paths to the catalog.
    """
    def __init__(self, default_extension=None):
        assert default_extension in ['.pkl', '.npz', '.npy', '.txt', None],\
            "Default extension must be .pkl, .npz, .npy, .txt, or None."
        self.default_extension = default_extension


    def act_on_cataloged_data(self, catalog, data_name, params,
                              extension=None):
        """Performs the defined action on a file within the catalog
        associated with a specific data_name and set of params.

        Not implemented for the Writer subclass of Actor.
        """
        raise NotImplementedError("You tried to use the "
                                  "`act_on_cataloged_data` method "
                                  "of the `Writer` class, but "
                                  "Writers are not designed to "
                                  "act on cataloged data.\nTry "
                                  "using the write_and_catalog_data "
                                  "method of the `Writer` class "
                                  "instead.")


    def act_on_catalog(self, catalog):
        """Since the writer writes _new_ files, it cannot act
        on all files in a catalog.
        """
        raise NotImplementedError("You tried to use the "
                                  "`act_on_cataloged_data` method "
                                  "of the `Writer` class, but "
                                  "Writers are not designed to "
                                  "act on catalogs:\nYou cannot "
                                  "write 'all files' to a catalog.\n"
                                  "Try using the write_and_catalog_data "
                                  "method of the `Writer` class "
                                  "within a loop instead.")


    def write_and_catalog_data(self, catalog,
                               data, data_name, params,
                               extension=None):
        """Saves the given data to a new file, and stores the filename
        together with the associated parameter in the file catalog.
        """
        if extension is None:
            extension = self.default_extension

        # Creating a new filename for the given data parameters
        filename = catalog.new_filename(data_name, params,
                                        extension)

        if filename is None:
            warnings.warn(f"Filename for {data_name} with params"
                          f" {params} is None. Skipping.")
            return

        # If pickling, write bytes to the new .pkl file
        if extension == '.pkl':
            with open(filename, 'wb') as file:
                pickle.dump(data, file)

        # If using numpy, write arrays to the new .npz file
        elif extension == '.npz':
            if isinstance(data, dict):
                np.savez(filename, **data)
            else:
                raise ValueError("Data must be a dictionary "
                                 "to be saved as a .npz file.")

        # Can also use .npy to save a single array
        elif extension == '.npy':
            np.save(filename, data)

        # Can write generic data to a text file
        elif extension == '.txt':
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(data)

        else:
            raise ValueError("Extension must be .pkl, .npz, .npy, or "
                             ".txt, "f"not {extension}.")
