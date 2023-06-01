from pathlib import Path
import os
import warnings
import datetime

# Importing time to wait if I run into `ScannerError`s
import time

# Data cataloging
import uuid
import yaml

# For loading catalog data:
import dill as pickle

# User input in case we find an existing file
from pytimedinput import timedInput


# =====================================
# Catalog Utilities
# =====================================
# ---------------------------------
# Catalog file utilities:
# ---------------------------------
def unique_filename(data_name, folder, file_extension):
    """Generate a unique filename for a given data type and source."""
    data_name = data_name.replace(' ', '-')
    unique_id = str(uuid.uuid4())
    return folder / f"{data_name}_{unique_id}.{file_extension}"


def dict_to_yaml_key(param_dict, pair_separator=' : ',
                     item_separator=' | '):
    """Takes a dictionary of parameters and turns it into a
    string that can be used as a key in a yaml file.
    """
    yaml_key = item_separator.join([
                    pair_separator.join([str(key), str(value)])
                    for key, value in sorted(param_dict.items())])
    return yaml_key


def ask_to_overwrite(name, default, timeout=10):
    """Ask the user if they want to overwrite an existing file,
    dir, etc.
    """
    default = default[0].lower()

    user_text, timed_out = timedInput(
            "\t(v)iew\t(o)verwrite\t(s)kip\t(c)ancel"
            +f"\n\t(current default: {default})",
            timeout=timeout)

    if timed_out:
        user_text = default

    if user_text == 'v':
        print("Opening for viewing...")
        os.system(f"open {name}")
        return ask_to_overwrite(name, default, timeout)
    if user_text == 'o':
        return True
    if user_text == 's':
        return False
    if user_text == 'c':
        raise KeyboardInterrupt

    print("Invalid input. Please try again.")
    return ask_to_overwrite(name, default, timeout)


# ---------------------------------
# Catalog param/key utilities:
# ---------------------------------
def check_if_recognized(data_name, recognized_data_names,
                        classification="data type",
                        warn_only=True):
    """Check if the data type is in a set of recognized
    data types.
    """
    recognized = (data_name in recognized_data_names)
    if warn_only and not recognized:
        warnings.warn(f"Unrecognized {classification}: {data_name}"
                      f"\n\t(Recognized {classification}s: "
                      f"{recognized_data_names})")
        return
    assert recognized, f"Unrecognized {classification}: {data_name}"\
                      +f"\n\t(Recognized {classification}s: "\
                      +f"{recognized_data_names})"


def check_params(params, warn_only=True):
    """Check if there are unexpected entries in the given params."""
    # We don't expect any `None`s in the values of params
    nones_in_values = "None" in params.values()\
        or None in params.values()

    if nones_in_values:
        if warn_only:
            warnings.warn("There are None values in the given params.")
            return
        assert False, "There are None values in the params."


def now():
    """Returns the current time in a standard format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



# =====================================
# Catalog Class
# =====================================
class Catalog:
    """In the Catalog class, we have an __init__ method that initializes
    the catalog with a given name and an empty list to store the file
    paths.

    The add_file method allows you to add a file to the catalog by
    providing its file path.

    The remove_file method removes a file from the catalog based on
    the provided file path.

    The get_files method returns the list of file paths in the catalog.

    The search_files method allows you to search for files in the
    catalog based on a given keyword. It iterates over the file paths
    in the catalog and adds any matching file paths to the
    matching_files list, which is then returned.

    You can use this Catalog class to create instances for different
    types of catalogs in your Librarian class, allowing you to organize
    files based on their types or any other criteria you choose.
    """
    def __init__(self, catalog_name, catalog_dir,
                 verbose: int = 1,
                 load: str = 'ask',
                 **kwargs):
        # Catalog information
        self.catalog_name = catalog_name
        self.catalog_dir = Path(catalog_dir)
        self.catalog_path = catalog_dir / f"{catalog_name}.yaml"

        # Information for this instance of the catalog
        self.verbose=verbose
        assert load in ['required', 'always', 'ask', 'never']

        # ---------------------------------
        # Loading
        # ---------------------------------
        # Load catalog if it exists
        if self.catalog_exists():
            if load in ['required', 'always']:
                self.load()
                return
            if load == 'ask':
                user_text, _ = timedInput(
                    "A catalog with this name "
                    +"already exists.\n"
                    +" Would you like to load it? (y/n)",
                    timeout=-1)
                if user_text.lower() == 'y':
                    self.load()
                    return
        elif self.catalog_serial_exists():
            if load in ['required', 'always']:
                self.load_serial()
                return
            if load == 'ask':
                user_text, _ = timedInput(
                    "A serialized catalog with this name "
                    +"already exists.\n"
                    +" Would you like to load it? (y/n)",
                    timeout=-1)
                if user_text.lower() == 'y':
                    self.load_serial()
                    return
        else:
            if load == 'required':
                raise FileNotFoundError(
                    f"Requested catalog {self.catalog_name} "
                    "does not exist.")

        # ---------------------------------
        # Initializing
        # ---------------------------------
        # Otherwise, initialize the catalog
        self.catalog_dict = {'name': catalog_name,
                             'directory': catalog_dir,
                             'catalog location':\
                                str(self.catalog_path),
                             'creation time': now(),
                             'last modified': now(),
                             'files': [],
                             'data_params': [],
                             }

        for key, value in kwargs.items():
            if key == 'recognized_names':
                self.catalog_dict['recognized names'] = value
            if key == 'recognized_extensions':
                self.catalog_dict['recognized extensions'] = value
            else:
                self.catalog_dict[key] = value

        self.yaml_header = ''
        self.update_yaml_header()
        self.catalog_dict['header'] = self.yaml_header

        # Save the catalog
        self.mkdir()
        self.save()


    def __str__(self):
        return self.yaml_header


    def catalog_exists(self):
        """Check if the catalog file exists."""
        return self.catalog_path.exists()


    def catalog_serial_exists(self):
        """Check if a serialization of the catalog exists."""
        serial_path = self.catalog_path.with_suffix(".pkl")
        return serial_path.exists()


    def mkdir(self):
        """Creates a catalog folder and associated file."""
        # Make catalog directory if it doesn't exist
        self.catalog_dir.mkdir(parents=True, exist_ok=True)


    def update_yaml_header(self):
        """Make the header for the catalog file."""
        self.last_modified = now()
        yaml_header = f"# {self.catalog_dict['name']} Catalog\n"\

        self.yaml_header = yaml_header
        return yaml_header


    def save(self):
        """Save the catalog to the catalog yaml file."""
        # Update the yaml header
        self.update_yaml_header()
        with open(self.catalog_path, 'w', encoding='utf8') as catalog:
            # Add a comment containing the header to the yaml file
            catalog.write(self.yaml_header)
            # Save the catalog
            yaml.safe_dump(self.catalog_dict, catalog,
                           width=float("inf"))


    def load(self):
        """Load the catalog from the catalog yaml file."""
        # Open the catalog
        with open(self.catalog_path, 'r', encoding='utf8') as catalog:
            catalog_dict = yaml.safe_load(catalog)
            self.catalog_dict = catalog_dict


    def save_serial(self):
        """Pickle the catalog and update the yaml file."""
        serial_path = self.catalog_path.with_suffix(".pkl")

        with open(serial_path, 'wb') as file:
            pickle.dump(self, file)


    def load_serial(self):
        """Load the catalog from an existing serialization."""
        serial_path = self.catalog_path.with_suffix(".pkl")
        with open(serial_path, 'rb') as file:
            loaded_catalog = pickle.load(file)

        # Copy over relevant attributes
        # (not including `self.verbose`)
        self.catalog_dict = loaded_catalog.catalog_dict

        # Clearing the loaded catalog from memory
        del loaded_catalog


    def new_filename(self, data_name: str, params: dict,
                     file_extension: str,
                     nested_folder: str = None,
                     default_overwrite_behavior: str = None):
        """Add a new entry to the example catalog file and returns
        the associated filename.
        """
        assert default_overwrite_behavior in ['overwrite', 'skip',
                                              'cancel', None],\
            "default_overwrite_behavior must be one of 'overwrite', "\
            "'skip', 'cancel', or None."

        # Verifying that the file extension and parameters are valid
        check_if_recognized(file_extension,
                            self.catalog_dict['recognized extensions'],
                            "file extension", warn_only=self.verbose < 1)
        check_params(params, warn_only=self.verbose < 1)

        # Checking if the data name is recognized
        check_if_recognized(data_name,
                            self.catalog_dict['recognized names'],
                            "data name", warn_only=self.verbose < 2)

        # Creating a unique filename within the requested folder
        if nested_folder is None:
            filename = unique_filename(data_name, self.catalog_dir,
                                       file_extension)
        else:
            # Create nested folder if it doesn't exist:
            nested_path = Path(self.catalog_dir / nested_folder)
            nested_path.mkdir(parents=True, exist_ok=True)

            # Generate a unique filename
            filename = unique_filename(data_name, nested_path,
                                       file_extension)

        # Adding the filename to the catalog
        with open(self.catalog_path, 'r', encoding='utf8') as catalog:
            # Attempting to open the catalog file
            open_attempts = 0
            while open_attempts < 12:
                try:
                    catalog_dict = yaml.safe_load(catalog)
                    break
                except yaml.scanner.ScannerError:
                    # Sometimes I run into `ScannerError`s when
                    # I try to run multiple jobs at once.
                    # I wonder if it's because two jobs are both trying
                    # to load and modify the data in the catalog file
                    print("\nRan into a ScannerError when attempting to"
                        f"load {params=}. Waiting before attempting again.")
                    # Keep trying for 12 attempts/60s total
                    open_attempts += 1
                    time.sleep(5)

            # Setting up dict structure if it does not already exist
            if catalog_dict is None:
                # First time only
                catalog_dict = {}
            if catalog_dict.get(data_name) is None:
                catalog_dict[data_name] = {}

            # Making a key for the yaml file
            yaml_key = dict_to_yaml_key(params)

            # Checking if the set of parameters already has an entry
            entry = catalog_dict[data_name].get(yaml_key)
            if entry is not None:
                file_path = Path(entry['filename'])
                if file_path.exists():
                    print("Existing file with the given parameters found."
                          "\n\tFile path: ", file_path,
                          "\n\tParameters: ", params,
                          "\n\tDate created: ", entry['date'],
                          "\n\nWould you still like to proceed?\n")

                    overwrite = ask_to_overwrite(filename,
                                         default_overwrite_behavior)
                    if not overwrite:
                        return None

            # Updating the dict with the given params and filenames
            params = dict({key: str(value)
                           for key, value in params.items()})
            catalog_dict[data_name][yaml_key] = params
            catalog_dict[data_name][yaml_key]['filename'] = str(filename)
            catalog_dict[data_name][yaml_key]['date added'] = str(now())

        # Storing the updated catalog
        if catalog_dict:
            # Storing the yaml file
            self.update_yaml_header()
            with open(self.catalog_path, 'w', encoding='utf8') as catalog:
                catalog.write(self.yaml_header)
                yaml.safe_dump(catalog_dict, catalog, width=float("inf"))
            # Updating class information
            self.catalog_dict['files'].append(filename)
            self.catalog_dict['data_params'].append( (data_name, params) )

            # and updating the serialization
            self.save()

        # Returning the filename
        return filename


    # ---------------------------------
    # Custodial utilities:
    # ---------------------------------
    def get_filename(self, data_name, params):
        """Retrieve a filename from the catalog dict"""
        # Verifying that the parameters are valid
        check_params(params, warn_only=self.verbose < 1)

        # Checking if the data name is recognized
        check_if_recognized(data_name,
                            self.catalog_dict['recognized names'],
                            "data name", warn_only=self.verbose < 2)

        if (data_name, params) not in self.catalog_dict['data_params']:
            raise FileNotFoundError(f"\n"
                "Could not find data name {data_name} and"
                f" params {params} in the catalog."
                "\nThe associated key in the catalog would "
                "have been:\n"
                +dict_to_yaml_key(params))

        # Returning the filename associated with the given name/params
        return self.catalog_dict['files'][\
                self.catalog_dict['data_params'].index((data_name, params))\
             ]


    def get_filename_from_yaml(self, data_name, params):
        """Retrieve a filename from the catalog yaml file."""
        # Getting info for the given params from the catalog
        yaml_key = dict_to_yaml_key(params)

        try:
            catalog_info = self.catalog_dict[data_name].get(yaml_key)
        except KeyError as error:
            warnings.warn(f"Ran into a KeyError: {error}")
            catalog_info = None

        if catalog_info is not None:
            return catalog_info['filename']

        raise FileNotFoundError(f"\n"
                "Could not find data name {data_name} and"
                f" params {params} in the catalog."
                "\nThe associated key in the catalog would "
                "have been:\n"
                +dict_to_yaml_key(params))


    def get_files(self):
        """Retrieve all files in the catalog."""
        return self.catalog_dict['files']


    def get_data_params(self):
        """Retrieve all data names and parameters in the catalog."""
        return self.catalog_dict['data_params']
