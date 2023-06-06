from pathlib import Path
import dill as pickle

from librarian.catalog import Catalog
from librarian.catalog import ask_to_overwrite

# TODO:
# Advanced Librarian also keeps track of useful actors <--> interface
# with GUI??


class Librarian:
    """
    In the Librarian class, we have an __init__ method that initializes
    the project and catalog locations, as well as empty dictionaries to store the file structure and project metadata.

    The add_file method allows you to add a file to the file structure
    by providing the file path and its associated metadata.

    The remove_file method removes a file from the file structure based
    on the provided file path.

    The update_metadata method allows you to update the metadata of a file
    in the file structure. You provide the file path, the metadata key to update, and the new value.

    The get_file_metadata method retrieves the metadata of a specific file
    in the file structure based on the provided file path.

    The set_project_metadata method allows you to set project-level metadata
    by providing a key-value pair.

    The get_project_metadata method returns the project metadata dictionary.
    """
    def __init__(self, location: str,
                 project_metadata: str = '',
                 catalog_folders: dict = None,
                 catalog_metadata: dict = None):
        # Project information
        self.location = Path(location)
        self.project_metadata = project_metadata

        # ---------------------------------
        # Catalog information
        # ---------------------------------
        # Folder locations as a dict of the form {name: dir}
        self.catalog_folders = catalog_folders

        # Catalog .yaml locations as a dict of the form {name: yaml}
        self.catalog_yamls = {cat_name: Path(cat_location) / f"{cat_name}.yaml"
                          for cat_name, cat_location in catalog_folders.items()}

        # Catalog metadata as a dict of the form {name: metadata}
        if catalog_metadata is not None:
            assert catalog_metadata.keys() == catalog_folders.keys(), \
                "Catalog structure and metadata keys must match."
            self.catalog_metadata = catalog_metadata
        else:
            self.catalog_metadata = {}


    def create_stacks(self, default_behavior='cancel', timeout=10):
        """Creates folders and files for each catalog in the library."""
        if self.location.exists():
            print("Catalog with the given name in the "
                  "given location exists!")
            if not ask_to_overwrite(self.location,
                                    default_behavior,
                                    timeout):
                return
        self.location.mkdir(parents=True, exist_ok=True)

        # Create catalogs/dirs with headers
        for catalog_name, catalog_dir in self.catalog_folders.items():
            self.add_catalog(catalog_name, catalog_dir,
                     metadata=self.catalog_metadata[catalog_name])

        # Create README.md
        self.write_readme()

        # pickle librarian object to location
        self.save()


    def save(self):
        """Pickle the librarian."""
        serial_path = self.location / 'librarian.pkl'
        with open(serial_path, 'wb') as file:
            pickle.dump(self, file)


    def load(self):
        """Loads the librarian object from a serialized file
        in self.location."""
        serial_path = self.location / 'librarian.pkl'
        with open(serial_path, 'rb') as file:
            temp_librarian = pickle.load(file)
        # Loading attributes while keeping new member variables
        self.__dict__.update(temp_librarian.__dict__)


    def write_readme(self):
        """Writes a README.md in self.location using
        project and catalog metadata.
        """
        readme_path = self.location / 'README.md'
        with open(readme_path, 'w', encoding='utf-8') as file:
            file.write(f"# README for Librarian at {self.location.name}\n\n")
            if self.project_metadata:
                file.write("## Project Metadata\n\n")
                for key, value in self.project_metadata.items():
                    file.write(f"- {key}: {value}\n")
            if self.catalog_folders:
                file.write("\n## Catalog Data\n\n")
                for catalog_name, folder in self.catalog_folders.items():
                    file.write(f"### {catalog_name}\n\n")
                    file.write(f"- Location: {folder}\n")
                    metadata = self.catalog_metadata.get(catalog_name, {})
                    for key, value in metadata.items():
                        file.write(f"- {key}: {value}\n")
                    file.write("\n")


    def add_catalog(self, catalog_name, catalog_dir,
                    metadata=None, default_behavior=None):
        """Adds a catalog to the library."""
        # Check existence of catalog .yaml file and
        # run by user if default_behavior is None
        catalog_dir = Path(catalog_dir)
        catalog_path = catalog_dir / f"{catalog_name}.yaml"
        if catalog_path.exists():
            print("Catalog with the given name in the "
                  "given location exists!")
            if not ask_to_overwrite(catalog_path, default_behavior):
                return

        # Attempting to initialize the catalog
        # (this creates a folder and .yaml for the catalog)
        Catalog(catalog_name, catalog_dir, **metadata)

        # Add catalog to catalog_folders
        self.catalog_folders[catalog_name] = catalog_dir
        self.catalog_yamls[catalog_name] = catalog_path
        if metadata is not None:
            self.catalog_metadata[catalog_name] = metadata


    def get_catalog_folders(self):
        """Returns a dictionary of catalog folders
        of the form {name: dir}.
        """
        return self.catalog_folders


    def get_catalog_metadata(self, catalog_name=None):
        """Returns catalog metadata for the given catalog
        name.
        If no name is given, returns a dictionary of
        the form {name: metadata}.
        """
        if catalog_name is None:
            return self.catalog_metadata
        if catalog_name in self.catalog_metadata:
            return self.catalog_metadata[catalog_name]

        # If neither is possible, return None
        print(f"Catalog '{catalog_name}' not found in the catalog metadata.")
        return None


    def get_project_metadata(self):
        """Returns the project metadata."""
        return self.project_metadata
