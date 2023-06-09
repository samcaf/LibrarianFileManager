"""This module defines the Actor class, which is a
base class with methods for performing actions on
files within a catalog.
"""

class Actor:
    """The Actor class serves as a base class for specific subclasses
    or implementations like "Plotters," "Loggers," "Converters," and
    others. It takes a catalog object as a parameter during initialization,
    allowing the actor to interact with the catalog and the files within the
    library.

    The act_on_file method is defined as an abstract method using the
    NotImplementedError. Subclasses must implement this method to define
    their specific action on a file. This method takes the file_path as a
    parameter and can perform any desired action on that file.

    The act_on_catalog method allows the actor to perform the defined action
    on all files within the catalog. It retrieves the list of file paths from
    the catalog and iterates over each file path, calling the act_on_file
    method for each file.

    To use the Actor class, you would create a subclass for each specific
    implementation (e.g., Plotter, Logger, Converter) that inherits from
    Actor and provides the implementation for the act_on_file method
    according to the specific behavior you want for that subclass.
    """
    def __init__(self):
        pass


    def file_action(self, file_path, **kwargs):
        """Defines an action to perform, given a file path.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement act_on_file method.")


    def act_on_cataloged_data(self, catalog, data_name, params,
                              **kwargs):
        """Performs the defined action on a file within the catalog
        associated with a specific data_name and set of params."""
        file_path = catalog.get_file(data_name, params,
                                     **kwargs)
        result = self.file_action(file_path)
        return result


    def act_on_catalog(self, catalog, **kwargs):
        """Perform the defined action on all files within the catalog."""
        file_paths = catalog.get_files()
        results = [self.file_action(file_path) for file_path in file_paths]
        return results


    def act(self, catalog, data_params=None, **kwargs):
        """Perform the defined action on all files within the catalog
        associated with a specific data_name and set of params."""
        if kwargs.get('data_params') is None:
            results = self.act_on_catalog(catalog, **kwargs)
        else:
            results = self.act_on_cataloged_data(catalog, *data_params,
                                                 **kwargs)
        return results


    def __call__(self, **kwargs):
        return self.act(**kwargs)
