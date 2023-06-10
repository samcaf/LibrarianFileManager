"""
The `actor` module provides classes for performing actions on files
within a catalog.

This module contains the following classes:
- `Actor`: Base class for performing actions on files within a catalog.
- Other specific actor subclasses can be defined in separate modules.

Usage:
1. Import the desired actor subclass from the module.
2. Instantiate the actor object, providing the necessary parameters.
3. Use the actor object to perform actions on files within a catalog.

See the Reader, Writer, and Plotter subclasses for examples.

Notes:
- The `Actor` class is designed to be subclassed to define specific actions on
  files.
- Specific actor subclasses can be implemented in separate modules for
  modularity.
- It is recommended to provide proper documentation for each actor subclass.
"""


class Actor:
    """Base class for performing actions on files within a catalog."""

    def __init__(self):
        pass

    def file_action(self, file_path, **kwargs):
        """
        Defines an action to perform on a file.

        Parameters
        ----------
        file_path : str
            The path of the file on which to perform the action.
        **kwargs
            Additional keyword arguments that can be used by subclasses.

        Returns
        -------
        Any
            The result of the file action.

        Raises
        ------
        NotImplementedError
            If the method is not implemented by subclasses.
        """
        raise NotImplementedError(
            "Subclasses must implement the file_action method."
        )

    def act_on_cataloged_data(self, catalog, data_name, params, **kwargs):
        """
        Performs the defined action on a file within the catalog.

        This method performs the defined action on a file within the catalog
        associated with a specific `data_name` and set of `params`.

        Parameters
        ----------
        catalog : Catalog
            The catalog containing the files.
        data_name : str
            The name of the data associated with the file.
        params : dict
            The parameters associated with the file.
        **kwargs
            Additional keyword arguments that can be used by subclasses.

        Returns
        -------
        Any
            The result of the file action.
        """
        file_path = catalog.get_file(
            data_name,
            params,
            **kwargs
        )
        result = self.file_action(file_path)
        return result

    def act_on_catalog(self, catalog, **kwargs):
        """
        Perform the defined action on all files within the catalog.

        This method performs the defined action on all files within the
        catalog.

        Parameters
        ----------
        catalog : Catalog
            The catalog containing the files.
        **kwargs
            Additional keyword arguments that can be used by subclasses.

        Returns
        -------
        list
            A list of results for each file action.
        """
        file_paths = catalog.get_files()
        results = [
            self.file_action(file_path)
            for file_path in file_paths
        ]
        return results

    def act(self, catalog, data_params=None, **kwargs):
        """
        Perform the defined action on files within the catalog.

        This method performs the defined action on files within the catalog.
        If `data_params` is provided, it performs the action on a specific
        file within the catalog based on the `data_params`. Otherwise, it
        performs the action on all files within the catalog.

        Parameters
        ----------
        catalog : Catalog
            The catalog containing the files.
        data_params : tuple or None, optional
            A tuple containing the `data_name` and `params` associated with
            a specific file.
            Defaults to None.
        **kwargs
            Additional keyword arguments that can be used by subclasses.

        Returns
        -------
        list
            A list of results for each file action.
        """
        if kwargs.get('data_params') is None:
            results = self.act_on_catalog(catalog, **kwargs)
        else:
            results = self.act_on_cataloged_data(
                catalog,
                *data_params,
                **kwargs
            )
        return results

    def __call__(self, **kwargs):
        """
        Perform the defined action on files within the catalog.

        This method is a convenience method that allows calling
        the `act` method by invoking the actor object itself.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments that can be used by subclasses.

        Returns
        -------
        list
            A list of results for each file action.
        """
        return self.act(**kwargs)
