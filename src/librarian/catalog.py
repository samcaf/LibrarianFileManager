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
    file_extension = file_extension.strip('.')
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
            +f"\n\t(current default: {default})\n\t",
            timeout=timeout)
    print("\n\n")

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
                        default_action="warn"):
    """Check if the data type is in a set of recognized
    data types.
    """
    recognized = (data_name in recognized_data_names)
    if default_action == "ignore":
        return recognized
    if default_action=="warn":
        if not recognized:
            warnings.warn(f"Unrecognized {classification}: {data_name}"
                          f"\n\t(Recognized {classification}s: "
                          f"{recognized_data_names})")
        return recognized
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
        self.catalog_path = self.catalog_dir / f"{catalog_name}.yaml"

        self._overwrite_behavior = kwargs.get('overwrite_behavior', 'skip')
        self._timeout = kwargs.get('timeout', 10)

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
                    "\tWould you like to load the existing "\
                    "catalog with the specified name "
                    f"{self.catalog_name}? (y/n)\n\t",
                    timeout=-1)
                print("\n\n")
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
                    f"Requested catalog `{self.catalog_name}` "
                    "does not exist.")

        # ---------------------------------
        # Initializing
        # ---------------------------------
        # Otherwise, initialize the catalog
        self._catalog_dict = {}
        self._catalog_dict['recognized names'] = kwargs.pop(
            'recognized_names', [])
        self._catalog_dict['recognized extensions'] = kwargs.pop(
            'recognized_extensions', [])

        for data_name in self._catalog_dict['recognized names']:
            self._catalog_dict[data_name] = {}

        self._catalog_dict.update(kwargs)
        self._catalog_dict.update({
                'name': catalog_name,
                'directory': str(catalog_dir),
                'catalog location': str(self.catalog_path),
                'creation time': str(now()),
                'last modified': str(now()),
                'files': [],
                'data_params': [],
         })

        # ---------------------------------
        # Saving
        # ---------------------------------
        self.mkdir()
        self.save()


    # =====================================
    # Overarching Catalog Methods
    # =====================================
    def __str__(self):
        return self.yaml_header()


    def dict(self):
        """Return the catalog as a dictionary."""
        return self._catalog_dict


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


    def yaml_header(self):
        """Make the header for the catalog file."""
        yaml_header  =  "# ---------------------------------\n"
        yaml_header += f"# Catalog for {self._catalog_dict['name']}\n"
        yaml_header +=  "# ---------------------------------\n"
        yaml_header += f"#\t- Location: {self._catalog_dict['catalog location']}\n"
        yaml_header += f"#\t- Recognized Names: {self._catalog_dict['recognized names']}\n"
        yaml_header +=  "#\t- Recognized Extensions: "\
                       f"{self._catalog_dict['recognized extensions']}\n"
        yaml_header += f"#\t- Created: {self._catalog_dict['creation time']}\n"
        yaml_header +=  "#\t- Last Modified: "\
                       f"{self._catalog_dict['last modified']}\n\n"

        return yaml_header


    def save(self):
        """Save the catalog to the catalog .yaml file."""
        # Update the yaml header
        with open(self.catalog_path, 'w', encoding='utf8') as catalog:
            # Add a comment containing the header to the yaml file
            catalog.write(self.yaml_header())
            # Save the catalog
            yaml.safe_dump(self._catalog_dict, catalog,
                           width=float("inf"))


    def load(self):
        """Load the catalog from the catalog .yaml file."""
        open_attempts = 0
        scanner_error = None

        while open_attempts < 12:
            with open(self.catalog_path, 'r', encoding='utf8') as catalog:
                try:
                    # Open the catalog
                    loaded_catalog = yaml.safe_load(catalog)
                    self._catalog_dict = loaded_catalog
                    return
                except yaml.scanner.ScannerError as error:
                    # Sometimes I run into `ScannerError`s when
                    # I try to run multiple jobs at once.
                    # I wonder if it's because two jobs are both trying
                    # to load and modify the data in the catalog file.
                    # Ideally, this would never happen, but if it does,
                    # just wait a bit and try again.
                    print("\nRan into a ScannerError when attempting to"
                          "load catalog. Waiting before attempting again.")
                    # Keep trying for 12 attempts/60s total
                    open_attempts += 1
                    time.sleep(5)
                    scanner_error = error
        raise yaml.scanner.ScannerError(scanner_error)



    def save_serial(self):
        """Pickle the catalog and update the yaml file."""
        serial_path = self.catalog_path.with_suffix(".pkl")

        with open(serial_path, 'wb') as file:
            pickle.dump(self, file)


    def load_serial(self):
        """Load the catalog from an existing serialization."""
        serial_path = self.catalog_path.with_suffix(".pkl")
        with open(serial_path, 'rb') as file:
            loaded_catalog_serial = pickle.load(file)

        # Copy over relevant attributes
        # (not including `self.verbose`)
        self._catalog_dict = loaded_catalog_serial.catalog_dict

        # Clearing the loaded catalog from memory
        del loaded_catalog_serial


    def set_overwrite_behavior(self, behavior, timeout=10):
        """Set the overwrite behavior for the catalog."""
        assert behavior in ['overwrite', 'skip', 'cancel', None],\
            "Overwrite behavior must be one of 'overwrite', "\
            "'skip', 'cancel', or None, rather than the"\
            f"given behavior {behavior}."

        self._overwrite_behavior = behavior
        self._timeout = timeout


    # =====================================
    # Main Functionality:
    # =====================================

    # ---------------------------------
    # Generating and Cataloging Filenames
    # ---------------------------------
    def new_filename(self, data_name: str, params: dict,
                     file_extension: str,
                     nested_folder: str = None):
        """Add a new entry to the example catalog file and returns
        the associated filename.
        """
        # Verifying that the file extension and parameters are valid
        check_if_recognized(file_extension,
                            self._catalog_dict['recognized extensions'],
                            "file extension",
                            default_action="warn")
        check_params(params, warn_only=self.verbose < 1)

        # Checking if the data name is recognized
        warn_behavior = "error"
        if self.verbose < 2:
            warn_behavior = "warn"
        if self.verbose < 1:
            warn_behavior = "ignore"
        check_if_recognized(data_name,
                            self._catalog_dict['recognized names'],
                            "data name",
                            default_action=warn_behavior)

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

        # Making a key to point to the new filename in the catalog
        yaml_key = dict_to_yaml_key(params)

        # Checking if the set of parameters already has an entry
        if self._catalog_dict.get(data_name) is None:
            # If this is the first time using this data_name,
            # create a new entry in the catalog
            self._catalog_dict[data_name] = {}
        entry = self._catalog_dict[data_name].get(yaml_key)

        if entry is not None:
            file_path = Path(entry['filename'])
            if file_path.exists():
                if self.verbose > 0:
                    print("Existing file with the given parameters found."
                          "\n\n\tFile path: ", file_path,
                          "\n\tParameters: ", params,
                          "\n\tDate created: ", entry['date added'],
                          "\n\n\tWould you still like to proceed?\n\t")

                    overwrite = ask_to_overwrite(filename, self._overwrite_behavior,
                                                 self._timeout)
                else:
                    # If the catalog is not verbose, just overwrite
                    overwrite = True

                # If the user doesn't want to overwrite the file,
                # return None
                if not overwrite:
                    return None
                # Otherwise, delete the old file and continue
                file_path.unlink()

        # Updating the dict with the given params and filenames
        params = dict({key: str(value) for key, value in params.items()})
        self._catalog_dict[data_name][yaml_key] = params
        self._catalog_dict[data_name][yaml_key]['filename'] = str(filename)
        self._catalog_dict[data_name][yaml_key]['date added'] = str(now())

        # Updating class information
        self._catalog_dict['files'].append(str(filename))
        self._catalog_dict['data_params'].append( (data_name, params) )
        self._catalog_dict['last modified'] = str(now())

        # Saving the updated catalog
        self.save()

        # Returning the filename
        return filename

    # ---------------------------------
    # Saving figures
    # ---------------------------------
    def savefig(self, fig, data_name: str, params: dict,
                file_extension: str = '.pdf',
                nested_folder: str = None,
                **kwargs):
        """Save a figure to the catalog."""
        filename = self.new_filename(data_name, params,
                                     file_extension,
                                     nested_folder)

        if filename is None:
            return

        fig.savefig(filename, **kwargs)
        return filename


    # =====================================
    # Custodial utilities:
    # =====================================
    def get_filename(self, data_name, params):
        """Retrieve a filename from the catalog dict"""
        # Verifying that the parameters are valid
        check_params(params, warn_only=self.verbose < 1)

        # Checking if the data name is recognized
        warn_behavior = "error"
        if self.verbose < 2:
            warn_behavior = "warn"
        if self.verbose < 1:
            warn_behavior = "ignore"
        check_if_recognized(data_name,
                            self._catalog_dict['recognized names'],
                            "data name",
                            default_action=warn_behavior)


        if (data_name, params) not in self._catalog_dict['data_params']:
            raise FileNotFoundError(f"\n"
                "Could not find data name {data_name} and"
                f" params {params} in the catalog."
                "\nThe associated key in the catalog would "
                "have been:\n"
                +dict_to_yaml_key(params))

        # Returning the filename associated with the given name/params
        return self._catalog_dict['files'][\
                self._catalog_dict['data_params'].index((data_name, params))\
             ]


    def get_filename_from_yaml(self, data_name, params):
        """Retrieve a filename from the catalog yaml file."""
        # Getting info for the given params from the catalog
        yaml_key = dict_to_yaml_key(params)

        try:
            catalog_info = self._catalog_dict[data_name].get(yaml_key)
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
        return self._catalog_dict['files']


    def get_data_params(self):
        """Retrieve all data names and parameters in the catalog."""
        return self._catalog_dict['data_params']
