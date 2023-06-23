"""This module defines the commandline_Writer class, which is designed to
write data to files using command line tools and store the filenames in a catalog.
"""
# Running command line commands
import os

# Tools for filename generation
from librarian.catalog import unique_filename

# Subclass of the Writer class
from librarian.actors.writer import Writer

# =====================================
# Commandline Writer Class
# =====================================

class commandline_Writer(Writer):
    """
    A class for writing data to files and storing the filenames in a
    catalog, where writing data is implemented through a command line
    command.

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


    # ---------------------------------
    # Commands and postprocessing
    # ---------------------------------
    def parameterized_command(self, file,
                              catalog, data_label, params,
                              **kwargs):
        """An abstract method representing a command line command
        obtained from the catalog and the parameters, given a
        uniquely generated filename.
        """
        # (to be implemented by subclass)
        raise NotImplementedError("The `get_command` method of the "
                    "`commandline_Writer` class is not implemented.")

    def postprocess(self, **kwargs):
        """An abstract method for any post-processing
        a user wants to do after running a command line
        command/tool.
        """
        # (to be implemented by subclass)
        print("No postprocessing performed.")


    # ---------------------------------
    # Writing data
    # ---------------------------------
    def write_and_catalog_data(self, catalog,
                               data_label, params,
                               extension='use_default',
                               **kwargs):
        """
        Save the given data to a new file and store the file
        together with the associated parameter in the file catalog.

        Parameters
        ----------
        catalog : Catalog
            The catalog object used to store the file paths.
        data_label : str
            The name of the data.
        params : dict
            The parameters associated with the data.
        """
        # If the given parameters are already cataloged, do nothing:
        if catalog.has_file(data_label=data_label, params=params):
            return

        # Otherwise, use a command line command to write the data:
        # (Use the default extension if none is provided)
        if extension == 'use_default':
            extension = self.default_extension

        # Generate a unique filename:
        folder = kwargs.get('folder', None)
        file = unique_filename(data_label, folder, extension)

        # Creating the command (must be implemented by subclass):
        command = self.parameterized_command(file=file,
                                             catalog=catalog,
                                             data_label=data_label,
                                             params=params,
                                             **kwargs)
        # Running the command if it exists:
        if command is None:
            return
        os.system(command)

        # If this succeeds, add the file to the catalog:
        catalog.add_file(file, data_label, params)

        # Postprocessing
        # (does nothing by default, but can be
        #  implemented by subclass):
        self.postprocess(file=file,
                         catalog=catalog,
                         data_label=data_label,
                         params=params,
                         **kwargs)
