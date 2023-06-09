"""This module contains the Catalog class, which is used to store
information about the files within a particular folder (the catalog)
and the metadata associated with those files.

The Catalog has several purposes, with the overaching purpose of
allowing users to easily create, maintain, update, and analyze
collections of files and their associated metadata.
  * It stores the file information and catalog metadata as a human-
    readable yaml file, which can be used to recreate the Catalog.
  * It allows the user to easily access and manipulate the files in
    the catalog and their metadata by providing the parameters
    associated with the files.
    For example:
      * It allows the user to easily add new files with unique
        filenames to the catalog.
      * It allows the user to easily update the metadata associated
        with the files in the catalog.
      * It ensure that duplicate files are not added to the catalog.
"""

from pathlib import Path
import os
import warnings
import datetime

# Importing TypedDict so that it can be used in defining
# the parameters which label files in the catalog.
from typing import TypedDict
# Importing inspect so that user can give classes as arguments
import inspect

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
# Utilities for Typed Parameters
# =====================================
def get_builtin(name):
    """Gets the builtin type with the given name, if
    it exists, and throws an AttributeError otherwise.

    Can be used to convert strings to types, e.g.
        get_builtin("int") --> int.

    The try-except statement is due to the fact
    that __builtins__ may be either a module or
    a dictionary, depending on context.
    See
        https://docs.python.org/3/library/builtins.html
    """
    if inspect.isclass(name):
        return name
    try:
        return __builtins__[name]
    except TypeError:
        return getattr(__builtins__, name)


def dict_to_typeddict(name, stringdict):
    """Converts a `key: type` dictionary to a
    TypedDict class with name `classname` whose keys are
    the keys of the input dictionary and whose types are
    the types specified by the dictionary values.
    The types can be given as strings, e.g. "int", "str".

    For example, if `stringdict` is
        {"a": "int", "b": "str", "c": "float"}
    the output will be a TypedDict class with the following
    signature:
        class classname(TypedDict):
            a: int
            b: str
            c: float
    """
    return TypedDict(name, {key: get_builtin(value)
                            for key, value in stringdict.items()})


def typeddict_to_stringdict(typeddict):
    """Converts the `parameter: type` dictionary of a TypedDict
    to a `parameter: type_as_string` dictionary.

    See https://stackoverflow.com/a/61944555
    """
    return {param_name: param_class.__name__
            for param_name, param_class
            in typeddict.__annotations__.items()}


def cast_as_typeddict(dictionary, typeddict):
    """Casts a dictionary as a given typeddict class.
    Also performs typechecking by checking that the
    list of keys for this typeddict instance is
    exactly the list of expected keys,
    with the expected types for the values
    associated with each key.
    """
    # Check that the dictionary has the correct keys
    assert set(dictionary.keys()) == \
        set(typeddict.__annotations__.keys()), \
        f"Invalid keys for {typeddict.__name__}:\n" \
        + f"\tExpected: {set(typeddict.__annotations__.keys())}\n" \
        + f"\tFound: {set(dictionary.keys())}"

    # Cast the dictionary to a typeddict and
    # check type validity element by element
    result = typeddict()

    for key, keytype in typeddict.__annotations__.items():
        try:
            result[key] = keytype(dictionary[key])
        except ValueError:
            raise ValueError(f"Invalid type for {key}: "
                             f"Expected {keytype}, "
                             f"found {type(dictionary[key])}")

    return result


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
            + f"\n\t(current default: {default})\n\t",
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
    if default_action == "warn":
        if not recognized:
            warnings.warn(f"Unrecognized {classification}: {data_name}"
                          f"\n\t(Recognized {classification}s: "
                          f"{recognized_data_names})")
        return recognized
    assert recognized, f"Unrecognized {classification}: {data_name}"\
        + "\n\t(Recognized classifications: "\
        + f"{recognized_data_names})"


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
                 load: str = 'ask',
                 **kwargs):
        # ---------------------------------
        # Global Catalog information
        # ---------------------------------
        self._catalog_name = catalog_name
        self._catalog_dir = Path(catalog_dir)
        self._catalog_path = self._catalog_dir / f"{catalog_name}.yaml"

        self._overwrite_behavior = kwargs.pop('overwrite_behavior', 'skip')
        self._timeout = kwargs.pop('timeout', 10)

        # ---------------------------------
        # Information for this instance of the catalog
        # ---------------------------------
        # Verbosity
        self.verbose = kwargs.pop('verbose', 1)

        # ---------------------------------
        # Loading
        # ---------------------------------
        # Whether/when to load the catalog from
        # an existing .yaml file
        assert load in ['required', 'always', 'ask', 'never'], \
            "`load` must be one of 'required', 'always', 'ask', or 'never'" \
            + f", not '{load}'."

        # Load catalog if it exists
        if self.catalog_exists():
            if load in ['required', 'always']:
                self.load()
                return
            if load == 'ask':
                user_text, _ = timedInput(
                    "\tWould you like to load the existing "
                    "catalog with the specified name "
                    f"{self._catalog_name}? (y/n)\n\t",
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
                    "already exists.\n"
                    " Would you like to load it? (y/n)",
                    timeout=-1)
                if user_text.lower() == 'y':
                    self.load_serial()
                    return
        else:
            if load == 'required':
                raise FileNotFoundError(
                    f"Requested catalog `{self._catalog_name}` "
                    "does not exist.")

        # ---------------------------------
        # Global parameter information
        # ---------------------------------
        # Parameters describing the cataloged information
        # fed in as a dictionary:
        # parameters = {param_name: param_type}
        parameters = kwargs.pop('parameters', None)
        if parameters is not None:
            assert isinstance(parameters, dict),\
                "Parameters must be a dictionary."
            self._typedparameterdict = dict_to_typeddict(
                    f"{catalog_name}_parameters", parameters)
        else:
            self._typedparameterdict = None

        # Defaults for the given parameters
        defaults = kwargs.pop('defaults', None)
        if defaults is not None:
            assert isinstance(defaults, dict),\
                "Defaults must be a dictionary."
            assert set(defaults.keys()).issubset(set(parameters.keys())),\
                "Parameters with default values must be a subset of "\
                "the given parameters."
            self._parameter_defaults = defaults
        else:
            self._parameter_defaults = {}


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
                'name': self._catalog_name,
                'directory': str(self._catalog_dir),
                'yaml location': str(self._catalog_path),
                'creation time': str(now()),
                'last modified': str(now()),
                'files': [],
                'data_params': [],
         })

        if self._typedparameterdict is not None:
            self._catalog_dict['parameter types'] = \
                typeddict_to_stringdict(self._typedparameterdict)

        if self._parameter_defaults is not None:
            self._catalog_dict['parameter defaults'] = \
                self._parameter_defaults

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


    def as_dict(self):
        """Return the catalog as a dictionary."""
        return self._catalog_dict


    def parameters_to_typeddict(self, parameters):
        """Takes the given set of parameters and
        converts them to a TypedDict instance."""
        if self._typedparameterdict is None:
            return parameters

        # Setting up the parameters with default values
        typedparameters = self._parameter_defaults.copy()
        typedparameters.update(parameters)

        # Casting to the TypeDict associated with this catalog
        # (and perform typechecking)
        typedparameters = cast_as_typeddict(typedparameters,
                                            self._typedparameterdict)

        return typedparameters


    def add_parameter(self, new_parameter,
                      parameter_type,
                      default_value=None):
        """Add a new parameter to the catalog."""
        # Making sure the parameter doesn't already exist
        if self._typedparameterdict is not None:
            existing_params = typeddict_to_stringdict(
                self._typedparameterdict)
            if new_parameter in existing_params:
                raise ValueError(f"Parameter {new_parameter} already "
                                 "exists; we don't support changing its "
                                 "default value or type to avoid problems "
                                 "with backwards compatibility or "
                                 "inconsistent labeling.")

        # Ensuring we use default values
        if default_value is None:
            raise ValueError("Must provide a default value "
                             "for the new parameter "
                             f"{new_parameter} to avoid "
                             "problems with backwards "
                             "compatibility.")

        # Preparing the typeddict if it doesn't exist
        if self._typedparameterdict is None:
            self._typedparameterdict = {}

        # Updating the TypedDict class constraining
        # the parameters of the catalog's files
        parameter_dict = typeddict_to_stringdict(
            self._typedparameterdict)
        parameter_dict.update({new_parameter: parameter_type})
        self._typedparameterdict = dict_to_typeddict(
            self._typedparameterdict.__name__, parameter_dict)

        # Updating the parameter defaults
        self._parameter_defaults.update({new_parameter: default_value})

        # Updating the catalog
        self.save()

        return

    def add_parameters(self, new_parameters, defaults=None):
        """Add the given parameters to the TypedDict
        describing the parameters associated with the
        catalog.

        Must be given a default value to avoid problems
        with backwards compatibility:
        the user should still be able to look for files
        associated with the old set of parameters without
        re-writing the entire catalog, so the default
        values are used to fill in the missing values
        for the old files.
        """
        if defaults is None:
            raise ValueError("Must provide default values "
                             "for new parameters to avoid "
                             "problems with backwards "
                             "compatibility.")
        if defaults.keys() != parameters.keys():
            raise ValueError("The defaults for the added parameters "
                             "must have the same keys as the "
                             "parameters being added.")
        # Updating this Catalog's TypedDict class
        for new_param, new_type in new_parameters.items():
            default = defaults.get(new_param)
            self.add_parameter(new_param, new_type, default)


    def catalog_exists(self):
        """Check if the catalog file exists."""
        return self._catalog_path.exists()


    def catalog_serial_exists(self):
        """Check if a serialization of the catalog exists."""
        serial_path = self._catalog_path.with_suffix(".pkl")
        return serial_path.exists()


    def mkdir(self):
        """Creates a catalog folder and associated file."""
        # Make catalog directory if it doesn't exist
        self._catalog_dir.mkdir(parents=True, exist_ok=True)


    def yaml_header(self):
        """Make the header for the catalog file."""
        yaml_header = "# ==========================================\n"
        yaml_header += f"# Catalog for {self._catalog_dict['name']}\n"
        yaml_header += "# ==========================================\n\n"
        yaml_header += "# ---------------------------------\n"
        yaml_header += "# Metadata:\n"
        yaml_header += "# ---------------------------------\n"
        yaml_header += "#\t- Catalog `.yaml` File Location:\n"
        yaml_header += f"#\t\t{self._catalog_dict['yaml location']}\n"
        yaml_header += "#\t- Recognized Names: \n"
        yaml_header += f"#\t\t{self._catalog_dict['recognized names']}\n"
        yaml_header += "#\t- Recognized Extensions:\n"\
                       f"#\t\t{self._catalog_dict['recognized extensions']}\n"
        yaml_header += "#\t- Created: "\
                       f"{self._catalog_dict['creation time']}\n"
        yaml_header += "#\t- Last Modified: "\
                       f"{self._catalog_dict['last modified']}\n\n"
        yaml_header += "# ---------------------------------\n"
        yaml_header += "# Parameters:\n"
        yaml_header += "# ---------------------------------\n"
        if self._typedparameterdict is not None:
            for param, param_type in \
                    self._typedparameterdict.__annotations__.items():
                yaml_header += f"#\t- {param}: {param_type} " \
                    f"(default: {self._parameter_defaults.get(param)})\n"
        else:
            yaml_header += "#\t- None provided (arbitrary parameters)\n"
        yaml_header += "\n# ==========================================\n\n"

        return yaml_header


    def save(self):
        """Save the catalog to the catalog .yaml file."""
        # Update the yaml header
        with open(self._catalog_path, 'w', encoding='utf8') as catalog:
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
            with open(self._catalog_path, 'r', encoding='utf8') as catalog:
                try:
                    # Open the catalog
                    loaded_catalog = yaml.safe_load(catalog)

                    # Access the loaded information
                    self._catalog_dict = loaded_catalog

                    # Set up the catalog's TypedDict class
                    self._typedparameterdict = \
                        self._catalog_dict.get('parameter types')
                    if self._typedparameterdict is not None:
                        self._typedparameterdict = \
                            dict_to_typeddict(
                                f"{self._catalog_name}_parameters",
                                self._typedparameterdict
                            )
                    self._parameter_defaults = \
                        self._catalog_dict.get('parameter defaults')

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
        serial_path = self._catalog_path.with_suffix(".pkl")

        with open(serial_path, 'wb') as file:
            pickle.dump(self, file)


    def load_serial(self):
        """Load the catalog from an existing serialization."""
        serial_path = self._catalog_path.with_suffix(".pkl")
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
        params = self.parameters_to_typeddict(params)

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
            filename = unique_filename(data_name, self._catalog_dir,
                                       file_extension)
        else:
            # Create nested folder if it doesn't exist:
            nested_path = self._catalog_dir / nested_folder
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

                    overwrite = ask_to_overwrite(filename,
                                                 self._overwrite_behavior,
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
        self._catalog_dict['data_params'].append((data_name, params))
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
        params = self.parameters_to_typeddict(params)

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
                                    "\nThe associated key in the catalog would"
                                    " have been:\n"
                                    + dict_to_yaml_key(params))

        # Returning the filename associated with the given name/params
        return self._catalog_dict['files'][
                self._catalog_dict['data_params'].index((data_name, params))
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
                                "\nThe associated key in the catalog would"
                                " have been:\n"
                                + dict_to_yaml_key(params))


    def get_files(self):
        """Retrieve all files in the catalog."""
        return self._catalog_dict['files']


    def get_data_params(self):
        """Retrieve all data names and parameters in the catalog."""
        return self._catalog_dict['data_params']
