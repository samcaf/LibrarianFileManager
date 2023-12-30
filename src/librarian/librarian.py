"""This module defines the Librarian class, which
is used to create a file structure associated with a
project and to manage the project's data at a coarse
grained level.

The Librarian class can be given a set of folders,
which will be used to store catalogs for different types
of information for the project.
"""

from pathlib import Path
import dill as pickle

from librarian.catalog import Catalog
from librarian.catalog import ask_to_overwrite

# Logging
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())


class Librarian:
    """
    The Librarian class manages the file structure and metadata of a project.

    Parameters
    ----------
    location : str
        The location of the project.
    project_metadata : str, optional
        Metadata associated with the project. Default is an empty string.
    catalog_folders : dict, optional
        The folder locations for each catalog in the library. Should be in
        the form {name: dir}. Default is None.
    catalog_metadata : dict, optional
        The catalog metadata in the form {name: metadata}. Default is None.
    catalog_parameters : dict, optional
        Parameters describing the data in each catalog. Should be in the form
        {name: parameters}. Default is None.

    Attributes
    ----------
    location : Path
        The location of the project.
    project_metadata : str
        Metadata associated with the project.
    catalog_folders : dict
        The folder locations for each catalog in the library in the
        form {name: dir}.
    catalog_yamls : dict
        The catalog .yaml file locations in the form {name: yaml}.
    catalog_parameters : dict
        Parameters describing the data in each catalog in the form
        {name: parameters}.
    catalog_metadata : dict
        The catalog metadata in the form {name: metadata}.
    """

    def __init__(self, location: str, project_metadata: str = '',
                 catalog_folders: dict = None,
                 catalog_metadata: dict = None,
                 catalog_parameters: dict = None,
                 catalog_default_parameters: dict = None):
        # Project information
        self.location = Path(location)
        self.project_metadata = project_metadata

        # ---------------------------------
        # Catalog information
        # ---------------------------------
        # Folder locations as a dict of the form {name: dir}
        self.catalog_folders = catalog_folders \
                               if catalog_folders is not None else {}

        # Catalog .yaml locations as a dict of
        # the form {name: yaml}
        self.catalog_yamls = {cat_name:
                              Path(cat_location) / f"{cat_name}.yaml"
                              for cat_name, cat_location
                              in self.catalog_folders.items()}

        # Parameters describing the data in each catalog
        self.catalog_parameters = {cat_name: None for cat_name
                                   in self.catalog_folders}
        if catalog_parameters is not None:
            self.catalog_parameters.update(catalog_parameters)

        if catalog_default_parameters is not None:
            self.catalog_default_parameters = \
                catalog_default_parameters
        else:
            self.catalog_default_parameters = {}

        # Catalog metadata as a dict of the form {name: metadata}
        self.catalog_metadata = {cat_name: {} for cat_name
                                 in self.catalog_folders}
        self.catalog_metadata.update(catalog_metadata)

        # Making the project location if it doesn't exist
        self.location.mkdir(parents=True, exist_ok=True)

    def create_stacks(self, save=False):
        """
        Creates folders and files for each catalog in
        slef.catalog_folders (defined at initialization).
        Named because it creates "stacks" for the "library".

        Parameters
        ----------
        save : bool, optional
            Whether to save a serialized version of
            the Librarian class instance associated
            with self after creating the stacks.
            Default is False.
        """
        # Create catalogs/dirs with headers
        for catalog_name, catalog_dir in self.catalog_folders.items():
            metadata = self.catalog_metadata.get(catalog_name)
            parameters = self.catalog_parameters.get(catalog_name)
            defaults = self.catalog_default_parameters.get(catalog_name)
            self.add_catalog(catalog_name, catalog_dir,
                             metadata=metadata,
                             parameters=parameters,
                             default_parameters=defaults)

        # Create README.md
        self.write_readme()

        # pickle librarian object to location
        if save:
            self.save()

    def save(self):
        """Pickle the librarian."""
        serial_path = self.location / 'librarian.pkl'
        with open(serial_path, 'wb') as file:
            pickle.dump(self, file)

    def load(self):
        """Loads the librarian object from a serialized file
        in self.location.
        """
        serial_path = self.location / 'librarian.pkl'
        with open(serial_path, 'rb') as file:
            temp_librarian = pickle.load(file)
        self.__dict__.update(temp_librarian.__dict__)

    def __str__(self):
        """
        Returns a string representation of the librarian; the form of
        this string is chosen for its use in generating a readme file.
        """
        string = f"# Librarian for '{self.location.name}'\n\n"
        if self.project_metadata:
            string += "## Project Metadata\n\n"
            for key, value in self.project_metadata.items():
                string += f"- {key}: {value}\n"
        if self.catalog_folders:
            string += "\n## Catalog Data\n"
            for catalog_name, folder in self.catalog_folders.items():
                string += "\n"
                string += f"### {catalog_name}\n"
                string += f"    - Location: '{folder}'\n"
                metadata = self.catalog_metadata[catalog_name].copy()
                description = metadata.pop('description', None)
                string += f"    - Description: {description}\n\n"
                for key, value in metadata.items():
                    string += f"    - {key}: {value}\n"
        return string

    def write_readme(self):
        """Writes a README.md in self.location using project and
        catalog metadata.
        """
        readme_path = self.location / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as file:
            file.write(str(self))

    def add_catalog(self, catalog_name, catalog_dir,
                    metadata=None, parameters=None,
                    default_parameters=None,
                    default_behavior='skip'):
        """Adds a catalog to the library.

        Parameters
        ----------
        catalog_name : str
            The name of the catalog.
        catalog_dir : str
            The directory where the catalog will be stored.
        metadata : dict, optional
            Metadata associated with the catalog. Default is None.
        parameters : dict, optional
            Parameters describing the data in the catalog. Default is None.
        default_behavior : str, optional
            The default behavior if the catalog already exists.
            Possible values are 'skip', 'overwrite', and 'ask'.
            Default is 'skip'.
        """
        # Check existence of catalog .yaml file and
        # run by user if default_behavior is None
        catalog_dir = Path(catalog_dir)
        catalog_path = catalog_dir / f"{catalog_name}.yaml"
        if catalog_path.exists():
            LOGGER.info("Catalog with the specified name "
                  f"{catalog_name} in the given location exists!")
            if not ask_to_overwrite(catalog_path, default_behavior):
                return

        # Attempting to initialize the catalog
        # (this creates a folder and .yaml for the catalog)
        catalog = Catalog(catalog_name, catalog_dir,
                          parameters=parameters,
                          default_parameters=default_parameters,
                          **metadata)

        # Add catalog to catalog_folders
        catalog.save()
        self.catalog_folders[catalog_name] = catalog_dir
        self.catalog_yamls[catalog_name] = catalog_path
        if metadata is not None:
            self.catalog_metadata[catalog_name] = metadata

    def get_catalog_folders(self):
        """
        Returns a dictionary of catalog folders in the form {name: dir}.

        Returns
        -------
        dict
            Dictionary of catalog folders.
        """
        return self.catalog_folders

    def get_catalog_metadata(self, catalog_name=None):
        """
        Returns catalog metadata for the given catalog name.

        Parameters
        ----------
        catalog_name : str, optional
            The name of the catalog to retrieve metadata from. If not provided, returns a dictionary of all catalog
            metadata. Default is None.

        Returns
        -------
        dict or None
            Catalog metadata or None if the catalog is not found.
        """
        if catalog_name is None:
            return self.catalog_metadata
        if catalog_name in self.catalog_metadata:
            return self.catalog_metadata[catalog_name]

        # If neither is possible, return None
        LOGGER.info(f"Catalog '{catalog_name}' not found in the catalog metadata.")
        return None

    def get_project_metadata(self):
        """
        Returns the project metadata.

        Returns
        -------
        str
            Project metadata.
        """
        return self.project_metadata
