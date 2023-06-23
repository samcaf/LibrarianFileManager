"""This module defines the Writer class, which is designed to
write data to files and store the filenames in a catalog.
"""

import warnings

# File storage
import dill as pickle
import numpy as np

# The Writer acts on files:
from librarian.actor import Actor


class Writer(Actor):
    """
    A class for writing data to files and storing the filenames in a catalog.

    This class provides methods to write data to files in various formats
    such as pickled files, NumPy files, and plain text files. It also supports
    adding the file paths to an associated catalog.

    Parameters
    ----------
    default_extension : str, optional
        The default file extension to use when writing files. Supported
        extensions are '.pkl', '.npz', '.npy', '.txt', and None.
        If None, the extension needs to be explicitly provided
        when writing a file. Default is None.

    Attributes
    ----------
    default_extension : str or None
        The default file extension to use when writing files.
    """

    def __init__(self, default_extension=None):
        assert default_extension in ['.pkl', '.npz', '.npy', '.txt', None], \
            "Default extension must be .pkl, .npz, .npy, .txt, or None."
        self.default_extension = default_extension

    def act_on_cataloged_data(self, catalog, data_label, params, extension=None):
        """
        Perform the defined action on a file within the catalog associated with
        a specific data_label and set of params.

        Not implemented for the Writer subclass of Actor.

        Raises
        ------
        NotImplementedError
            If this method is called, as Writers are not designed to act
            on cataloged data.
        """
        raise NotImplementedError("You tried to use the "
                                  "`act_on_cataloged_data` method "
                                  "of the `Writer` class, "
                                  "but Writers are not designed to "
                                  "act on cataloged data. Try using the "
                                  "write_and_catalog_data method of "
                                  "the `Writer` class instead.")

    def act_on_catalog(self, catalog):
        """
        Since the writer writes new files, it cannot act on
        all files in a catalog.

        Raises
        ------
        NotImplementedError
            If this method is called, as Writers are not designed
            to act on catalogs.
        """
        raise NotImplementedError("You tried to use the "
                                  "`act_on_cataloged_data` method "
                                  "of the `Writer` class, "
                                  "but Writers are not designed to "
                                  "act on catalogs. You cannot write "
                                  "'all files' to a catalog.\n\n"
                                  "Try using the write_and_catalog_data"
                                  " method of the `Writer` "
                                  "class within a loop instead.")

    def write_and_catalog_data(self, catalog, data, data_label, params,
                               extension=None):
        """
        Save the given data to a new file and store the filename
        together with the associated parameter in the file catalog.

        Parameters
        ----------
        catalog : Catalog
            The catalog object used to store the file paths.
        data : object
            The data to be written to the file.
        data_label : str
            The name of the data.
        params : dict
            The parameters associated with the data.
        extension : str, optional
            The file extension to use for the file.
            Default is None.
            If None, the default_extension attribute of
            the Writer class will be used.

        Raises
        ------
        ValueError
            If the file extension is not supported.
        """
        if extension is None:
            extension = self.default_extension

        filename = catalog.new_filename(data_label, params, extension)

        if filename is None:
            warnings.warn(f"Filename for {data_label} with params "
                          f"{params} is None. Skipping.")
            return

        if extension == '.pkl':
            with open(filename, 'wb') as file:
                pickle.dump(data, file)
        elif extension == '.npz':
            if isinstance(data, dict):
                np.savez(filename, **data)
            else:
                raise ValueError("Data must be a dictionary to be "
                                 "saved as a .npz file.")
        elif extension == '.npy':
            np.save(filename, data)
        elif extension == '.txt':
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(data)
        else:
            raise ValueError("Extension must be .pkl, .npz, .npy, "
                             f"or .txt, not {extension}.")
