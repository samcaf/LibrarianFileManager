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


def stringdict_to_typeddict(name, stringdict):
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
    if not hasattr(typeddict, '__annotations__'):
        raise TypeError("Input must be a TypedDict or"
                        "dict-like object with __annotations__,"
                        f"but was instead {type(typeddict)}")
    return {param_name: param_class.__name__
            for param_name, param_class
            in typeddict.__annotations__.items()}


def cast_as_typeddict(dictionary, typeddict,
                      defaults=None,
                      allow_undeclared_keys=False):
    """Casts a dictionary into the form associated with
    the given typeddict class.

    Allows for default values to be given missing keys,
    and for extra keys to be included.

    Also performs typechecking by checking that the
    list of keys for this typeddict instance is
    exactly the list of expected keys,
    with the expected types for the values
    associated with each key.
    """
    # Setting up default values
    if defaults is None:
        defaults = {}

    keys_with_defaults = set(defaults.keys())

    # If we are not given a TypedDict for type checking
    # we must "allow extra keys" because we expect
    # no keys by default
    if typeddict is None:
        if allow_undeclared_keys:
            result = defaults
            result.update(dictionary)
            return result
        # Otherwise, raise an error
        raise ValueError("Must specify a TypedDict "
                         "class for typechecking if "
                         "allow_undeclared_keys is False.")

    # Expected and given dictionary keys
    expected_keys = set(typeddict.__annotations__.keys())
    found_keys = set(dictionary.keys())
    tdict_name = typeddict.__name__

    # (the keys with default values are not required)
    all_given_keys = found_keys.union(keys_with_defaults)

    if not allow_undeclared_keys:
        # If we only accept the pre-defined keys
        # defined for the typeddict
        if expected_keys != all_given_keys:
            raise ValueError(
                f"Expected keys for {tdict_name}:"
                f"\n\t{expected_keys}."
                f"\nFound keys:\n\t{found_keys}"
                "\n\nFound-Expected:"
                f"\n\t{found_keys - expected_keys}"
                "\nExpected-Found:"
                f"\n\t{expected_keys - found_keys}\n\n"
                "(The option `allow_undeclared_keys` can be set to True "
                "to allow extra keys that were not expected)."
            )
    else:
        if not expected_keys.issubset(all_given_keys):
            # If we allow extra keys, then we only check that
            # the expected keys are a subset of the found keys
            raise ValueError(
                f"Expected keys for {tdict_name}:"
                f"\n\t{expected_keys}."
                f"\nFound keys:\n\t{found_keys}"
                "\nExpected-Found:"
                f"\n\t{expected_keys - found_keys}\n\n"
                "(The option `allow_undeclared_keys` can be set to False "
                "to prevent extra keys that were not expected)."
            )

    # Cast the dictionary to a typeddict and
    # check type validity element by element
    result = typeddict()

    # Putting in default values
    for key, value in defaults.items():
        result[key] = value

    # Putting in given/found values
    for key, value in dictionary.items():
        result[key] = value

    # Performing type checking/type converting for
    # any of the given keys which are defined within
    # the typeddict
    for key, keytype in typeddict.__annotations__.items():
        if keytype == get_builtin(bool) and \
                isinstance(result[key], str):
            if result[key].lower() in ['true', 't', '1']:
                result[key] = True
            elif result[key].lower() in ['false', 'f', '0']:
                result[key] = False
            else:
                raise ValueError("Invalid value "
                    f"{result[key]} for casting"
                    " to bool.")
        elif keytype == get_builtin(list) and \
                isinstance(result[key], str):
            if ',' in result[key]:
                result[key] = [val.strip(' ') for val in
                              result[key].split(',')]
            else:
                result[key] = result[key].split(' ')
        else:
            try:
                result[key] = keytype(result[key])
            except ValueError as exc:
                raise ValueError(str(exc) +
                                 f"Invalid type for {key}: "
                                 f"Expected {keytype}, "
                                 f"found {type(result[key])}")\
                    from exc
            except TypeError as exc:
                raise TypeError(str(exc) +
                                f"({key=}, {keytype=})")\
                    from exc

    return result


# =====================================
# Catalog Utilities
# =====================================
# ---------------------------------
# Catalog file utilities:
# ---------------------------------
def unique_filename(label, folder, file_extension):
    """Generate a unique filename for a given data name."""
    label = label.replace(' ', '-')
    unique_id = str(uuid.uuid4())

    # Setting up the filename
    if file_extension is None:
        filename = f"{label}_{unique_id}"
    else:
        file_extension = file_extension.lstrip('.')
        filename = f"{label}_{unique_id}.{file_extension}"

    # Returning the filepath
    # (includes the folder if it is not None)
    if folder is None:
        folder = ''
    return os.path.join(folder, filename)


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
def check_if_recognized(label, recognized_labels,
                        classification="data type",
                        default_action="warn"):
    """Check if the data type is in a set of recognized
    data types.
    """
    recognized = (label in recognized_labels)
    if default_action == "ignore":
        return recognized
    if default_action == "warn":
        if not recognized:
            warnings.warn(f"Unrecognized {classification}: {label}"
                          f"\n\t(Recognized {classification}s: "
                          f"{recognized_labels})")
        return recognized
    assert recognized, f"Unrecognized {classification}: {label}"\
        + "\n\t(Recognized classifications: "\
        + f"{recognized_labels})"


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

    The search_files method allows you to search for files in the
    catalog based on a given keyword. It iterates over the file paths
    in the catalog and adds any matching file paths to the
    matching_files list, which is then returned.

    You can use this Catalog class to create instances for different
    types of catalogs in your Librarian class, allowing you to organize
    files based on their types or any other criteria you choose.

    Methods:
        TODO: Add methods to docstring
    """

    # ####################################
    # Initialization
    # ####################################
    # * Creating the catalog from scratch --
    #   either creating a directory and .yaml file
    #   or loading from a .yaml file
    #
    # * Setting up tools for type checking and
    #   type conversion of parameters associated
    #   with catalog entries
    def __init__(self, catalog_name, catalog_dir,
                 load: str = 'ask',
                 **kwargs):
        # ---------------------------------
        # Global Catalog information
        # ---------------------------------
        self._catalog_name = catalog_name
        self._catalog_dir = Path(catalog_dir)
        self._catalog_path = self._catalog_dir / f"{catalog_name}.yaml"

        # ---------------------------------
        # Information for this instance of the catalog
        # ---------------------------------
        # Behavior when encountering existing files
        self._overwrite_behavior = kwargs.pop('overwrite_behavior', 'skip')
        self._timeout = kwargs.pop('timeout', 10)

        # Verbosity
        self._verbose = kwargs.pop('verbose', 1)

        # Strictness when parsing parameters
        #
        # Fixing whether the catalog allows for parameters
        # which were not specified during initialization
        # (False by default)
        # This describes how "strict" the catalog is
        # in terms of the parameters it accepts
        # (i.e. default is strict)

        # For convenience in initialization, allowing either
        # "allow_undeclared_parameters" or "strict"
        # as keyword arguments to specify this behavior
        lenient = kwargs.get(
            'allow_undeclared_parameters', None)
        strict = kwargs.get('strict', None)

        # If neither is provided, default to strict behavior
        if lenient is None and strict is None:
            self._allow_undeclared_parameters = False

        # If both are provided and they are not opposite,
        # raise an error
        elif lenient is not None and strict is not None:
            if lenient == strict:
                raise ValueError(
                    "Cannot set both `allow_undeclared_parameters` "
                    "and `strict` to the same values.\n"
                    "`allow_undeclared_parameters` reflects "
                    "the 'leniency' of the catalog in terms of "
                    "the parameters it accepts.\n")

        # Otherwise, set the value to the provided one
        else:
            self._allow_undeclared_parameters = \
                bool(lenient) or not bool(strict)


        # ---------------------------------
        # Loading
        # ---------------------------------
        # Whether/when to load the catalog from
        # an existing .yaml file
        assert load in ['required', 'always', 'ask', 'never'], \
            "`load` must be one of 'required', 'always', 'ask', or 'never'" \
            + f", not '{load}'."

        # Load catalog if it exists
        # and if we might want to load
        # the catalog
        if self.catalog_exists() and load != 'never':
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
            self._typedparameterdict = stringdict_to_typeddict(
                    f"{catalog_name}_parameters", parameters)
        else:
            self._typedparameterdict = None

        # Defaults for the given parameters
        # (i.e. defining optional parameters)
        default_parameters = kwargs.pop('default_parameters', None)
        if default_parameters is not None:
            assert isinstance(default_parameters, dict),\
                "default_parameters must be a dictionary."
            assert set(default_parameters.keys()).issubset(
                    set(parameters.keys())),\
                "Parameters with default values must be a subset of "\
                "the given expected parameters."
            self._default_parameters = default_parameters
        else:
            self._default_parameters = {}

        # ---------------------------------
        # Initializing
        # ---------------------------------
        # Otherwise, initialize the catalog

        # Universal catalog properties
        self._catalog_dict = {}

        # Setting up recognized names/extensions
        for key in ['recognized_names',
                    'recognized_extensions']:
            val = kwargs.get(key, {})
            if isinstance(val, str):
                val = val.lstrip('[').rstrip(']')
                val = val.split(',')
                val = [v.strip() for v in val]
            key = key.replace('_', ' ')
            self._catalog_dict[key] = val

        self._catalog_dict['description'] = kwargs.pop('description')

        for data_label in self._catalog_dict['recognized names']:
            self._catalog_dict[data_label] = {}

        # Additional properties
        self._catalog_dict.update(kwargs)
        self._catalog_dict.update({
                'name': self._catalog_name,
                'directory': str(self._catalog_dir),
                'yaml location': str(self._catalog_path),
                'creation time': str(now()),
                'last modified': str(now()),
                'files': [],
                '(data_label, parameter) pairs': [],
         })

        # ---------------------------------
        # How parameters are handled
        # ---------------------------------
        # TypedDict for converting given parameters
        # to the correct type (i.e. from input strings)
        self._catalog_dict['parameter types'] = \
            parameters

        # Default parameters
        self._catalog_dict['default parameters'] = \
            self._default_parameters

        # ---------------------------------
        # Saving
        # ---------------------------------
        self.mkdir()
        self.save()


    # ####################################
    # Overarching Catalog Methods
    # ####################################
    # =====================================
    # Catalog metadata
    # =====================================
    def __str__(self):
        return self.yaml_header()

    def as_dict(self):
        """Return the catalog as a dictionary."""
        return self._catalog_dict

    def name(self):
        """Returns the catalog name."""
        return self._catalog_name

    def dir(self):
        """Returns the catalog directory."""
        return self._catalog_dir

    def mkdir(self):
        """Creates a catalog folder and associated file.
        (for use during __init__)"""
        # Make catalog directory if it doesn't exist
        self._catalog_dir.mkdir(parents=True, exist_ok=True)

    def catalog_exists(self):
        """Check if the catalog file exists."""
        return self._catalog_path.exists()

    def catalog_serial_exists(self):
        """Check if a serialization of the catalog exists."""
        serial_path = self._catalog_path.with_suffix(".pkl")
        return serial_path.exists()

    def set_overwrite_behavior(self, behavior, timeout=10):
        """Set the overwrite behavior for the catalog."""
        assert behavior in ['overwrite', 'skip', 'cancel', None],\
            "Overwrite behavior must be one of 'overwrite', "\
            "'skip', 'cancel', or None, rather than the"\
            f"given behavior {behavior}."

        self._overwrite_behavior = behavior
        self._timeout = timeout


    # =====================================
    # Saving and loading
    # =====================================
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

                    # Setting up recognized names/extensions
                    for key in ['recognized names',
                                'recognized extensions']:
                        val = loaded_catalog.get(key)
                        if isinstance(val, str):
                            val = val.lstrip('[').rstrip(']')
                            val = val.split(',')
                            val = [v.strip() for v in val]
                            self._catalog_dict[key] = val

                    # Set up the catalog's TypedDict class
                    self._typedparameterdict = \
                        self._catalog_dict.get('parameter types')
                    if self._typedparameterdict is not None:
                        self._typedparameterdict = \
                            stringdict_to_typeddict(
                                f"{self._catalog_name}_parameters",
                                self._typedparameterdict
                            )

                    self._default_parameters = \
                        self._catalog_dict.get('default parameters')
                    # Should never be None, since it is
                    # initialized to {}
                    assert self._default_parameters is not None,\
                        "Catalog must have a (possibly empty) "\
                        "dict of default parameters."

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


    def yaml_header(self):
        """Make the header for the catalog file."""
        yaml_header = "# ==========================================\n"
        yaml_header += f"# Catalog for {self._catalog_dict['name']}\n"
        yaml_header += "# ==========================================\n"
        yaml_header += f"# Description:\n"
        yaml_header += f"#\t{self._catalog_dict['description']}\n\n"
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
        yaml_header += "# Expected Parameters:\n"
        yaml_header += "# ---------------------------------\n"
        if self._typedparameterdict is not None:
            for param, param_type in \
                    self._typedparameterdict.__annotations__.items():
                yaml_header += f"#\t- {param}: {param_type} "
                if param in self._default_parameters:
                    yaml_header += f"(default: "\
                                   f"{self._default_parameters[param]})\n"
        else:
            yaml_header += "#\t- None provided (arbitrary parameters)\n"
        yaml_header += "\n# ==========================================\n\n"

        return yaml_header


    # ---------------------------------
    # Serialization
    # ---------------------------------
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
        # (not including `self._verbose`)
        self._catalog_dict = loaded_catalog_serial.catalog_dict

        # Clearing the loaded catalog from memory
        del loaded_catalog_serial


    # ####################################
    # Main Functionality:
    # ####################################

    # =====================================
    # Generating and Cataloging Filenames
    # =====================================
    def new_filename(self, data_label: str, params: dict,
                     file_extension: str,
                     nested_folder: str = None,
                     filename: str = None,
                     warn_behavior: str = None):
        """Add a new entry to the example catalog file and returns
        the associated filename.
        """
        # Type checking/type casting the given parameters
        params = self.configure_parameters(params)

        # Checking to see if all provided information
        # is consistent with what the catalog expects
        # to be given
        if warn_behavior is None:
            warn_behavior = "error"
            if self._verbose < 2:
                warn_behavior = "warn"
            if self._verbose < 1:
                warn_behavior = "ignore"

        # Verifying that the file extension and parameters are valid
        check_if_recognized(file_extension,
                            self._catalog_dict['recognized extensions'],
                            "file extension",
                            default_action=warn_behavior)

        # Checking if the data name is recognized

        check_if_recognized(data_label,
                            self._catalog_dict['recognized names'],
                            "data name",
                            default_action=warn_behavior)

        # Creating a unique filename within the requested folder
        if filename is None:
            if nested_folder is None:
                file_dir = self._catalog_dir
            else:
                # Create nested folder if it doesn't exist:
                nested_path = self._catalog_dir / nested_folder
                nested_path.mkdir(parents=True, exist_ok=True)
                file_dir = nested_path
            # Generate a unique filename
            filename = unique_filename(data_label, file_dir,
                                       file_extension)

        # Making a key to point to the new filename in the catalog
        yaml_key = dict_to_yaml_key(params)

        # Checking if the set of parameters already has an entry
        if self._catalog_dict.get(data_label) is None:
            # If this is the first time using this data_label,
            # create a new entry in the catalog
            self._catalog_dict[data_label] = {}
        entry = self._catalog_dict[data_label].get(yaml_key)

        if entry is not None:
            file_path = Path(entry['filename'])
            if file_path.exists():
                if self._verbose > 0:
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

                # Otherwise, delete the old file associated
                # with this data label and this set of
                # parameters and continue
                self.remove_file(filename=None,
                         data_label=data_label, params=params,
                         delete_file=True)

        # Updating the dict with the given params and filenames
        params = dict({key: str(value) for key, value in params.items()})
        self._catalog_dict[data_label][yaml_key] = params

        # Updating class information
        self._catalog_dict['files'].append(str(filename))
        saved_params = params.copy()
        self._catalog_dict['(data_label, parameter) pairs'].append(
                (data_label, saved_params))
        self._catalog_dict['last modified'] = str(now())

        # Adding filename and date added to catalogued file
        self._catalog_dict[data_label][yaml_key]['filename'] = str(filename)
        self._catalog_dict[data_label][yaml_key]['date added'] = str(now())

        # Saving the updated catalog
        self.save()

        # Returning the filename
        return filename

    def add_file(self, filename: str,
                 data_label: str, params: dict):
        """An application of `new_filename` which simply takes in
        a filename, data_label, and parameters and adds them to the
        catalog.

        Ignores any warnings about unrecognized parameters or
        file extensions.
        """
        return self.new_filename(data_label=data_label,
                                 params=params,
                                 file_extension=None,
                                 nested_folder=None,
                                 filename=filename,
                                 warn_behavior="ignore")

    def remove_file(self, filename: str,
                    data_label: str = None, params: dict = None,
                    delete_file: bool = True,
                    save: bool = True):
        """Removes a file from the catalog."""
        # Checking if the file exists
        if not self.has_file(filename=filename,
                             data_label=data_label, params=params):
            raise FileNotFoundError(f"File {filename} not found in catalog.")

        # Getting the file path
        yaml_key = ''
        if filename is None:
            yaml_key = dict_to_yaml_key(params)
            filename = self._catalog_dict[data_label][yaml_key]['filename']
        else:
            yaml_key = self.get_yaml_key(filename)
            data_label, params = self.get_data_label_params(filename)

        # Deleting the file
        if delete_file:
            file_path = Path(filename)
            file_path.unlink()
            del file_path

        # Removing the file metadata from the catalog
        index = self._catalog_dict['files'].index(filename)
        del self._catalog_dict['files'][index]
        del self._catalog_dict['(data_label, parameter) pairs'][index]
        self._catalog_dict[data_label].pop(yaml_key)

        # Updating the catalog
        if save:
            self._catalog_dict['last modified'] = str(now())
            self.save()


    def purge(self):
        """Removes all files from the catalog."""
        for filename in self._catalog_dict['files']:
            self.remove_file(filename=filename, save=False)
        self._catalog_dict['files'] = []
        self._catalog_dict['(data_label, parameter) pairs'] = []
        self._catalog_dict['last modified'] = str(now())
        self.save()


    # =====================================
    # Saving figures
    # =====================================
    def savefig(self, fig, data_label: str, params: dict,
                file_extension: str = '.pdf',
                nested_folder: str = None,
                **kwargs):
        """Save a figure to the catalog."""
        filename = self.new_filename(data_label, params,
                                     file_extension,
                                     nested_folder)

        if filename is None:
            return

        fig.savefig(filename, **kwargs)
        return filename


    # ####################################
    # Custodial utilities:
    # ####################################

    # =====================================
    # Parameters
    # =====================================

    # ---------------------------------
    # Configuring parameters
    # ---------------------------------
    def configure_parameters(self, parameters):
        """Takes the given set of parameters and
        converts them to a TypedDict instance.

        Fills the default parameters with the given
        parameters, if they are not already filled.
        """
        if self._typedparameterdict is None:
            # If there are no defined parameters/types,
            # just return the given parameters
            return parameters

        # Setting up the parameters with default values
        typedparameters = self._default_parameters.copy()
        typedparameters.update(parameters)

        # Casting to the TypeDict associated with this catalog
        # (and perform typechecking)

        typedparameters = cast_as_typeddict(
                            # Given params as a dict
                            dictionary=typedparameters,
                            # TypedDict for typechecking
                            typeddict=self._typedparameterdict,
                            # Default parameters from init
                            defaults=self._default_parameters,
                            # Whether to allow undefined params
                            allow_undeclared_keys=self._allow_undeclared_parameters)

        return typedparameters


    def add_parameter(self, new_parameter,
                      parameter_type,
                      default_value=None):
        """Add a new parameter with a default value to the catalog."""
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
        self._typedparameterdict = stringdict_to_typeddict(
            self._typedparameterdict.__name__, parameter_dict)

        # Updating the default parameters
        self._default_parameters.update({new_parameter: default_value})

        # Updating the catalog
        self.save()

        return


    def add_parameters(self, new_parameters,
                       defaults=None):
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
        if defaults.keys() != new_parameters.keys():
            raise ValueError("The defaults for the added parameters "
                             "must have the same keys as the "
                             "parameters being added.")
        # Updating this Catalog's TypedDict class
        for new_param, new_type in new_parameters.items():
            default = defaults.get(new_param)
            self.add_parameter(new_param, new_type, default)


    # ---------------------------------
    # Other parameter metadata
    # ---------------------------------
    # Expected parameters
    def expected_parameters(self):
        """Returns the set of expected parameters
        for the catalog.
        """
        return self._typedparameterdict.__annotations__.keys()

    def expected_parameter_types(self):
        """Returns the expected types for each
        expected parameter.
        """
        return self._typedparameterdict.__annotations__


    # Required parameters
    def required_parameters(self):
        """Returns the set of required parameters
        for the catalog.
        """
        parameters = self.expected_parameters()
        optional_parameters = self.optional_parameters()
        [parameters.remove(param)
         for param in optional_parameters]
        return parameters

    def required_parameter_types(self):
        """Returns the expected types for each
        required parameter.
        """
        parameter_types = self.expected_parameter_types()
        optional_parameters = self.optional_parameters()
        [parameter_types.pop(param)
         for param in optional_parameters]
        return parameter_types


    # Optional parameters (parameters with default values)
    def optional_parameters(self):
        """Returns the set of optional parameters
        for the catalog.
        """
        return self._default_parameters.keys()

    def optional_parameter_types(self):
        """Returns the expected types for each
        optional parameter.
        """
        return {key: self._typedparameterdict.__annotations__[key]
                for key in self._default_parameters.keys()}

    def optional_parameter_values(self):
        """Returns the default values for each
        optional parameter.
        """
        return self._default_parameters

    def parameter_defaults(self):
        """Return the default parameters."""
        return self._default_parameters

    def default_parameters(self):
        """Return the default parameters."""
        return self._default_parameters


    # =====================================
    # Utilities for perusing the catalog
    # =====================================
    # ---------------------------------
    # Files
    # ---------------------------------
    def get_files(self):
        """Retrieve all files in the catalog."""
        return self._catalog_dict['files']

    def has_file(self, filename=None, data_label=None, params=None):
        """Checks if a file exists in the catalog:
        returns true if the file exists and false if it does not.
        """
        exactly_one_none = (filename is None) ^ (data_label is None)
        if not exactly_one_none:
            raise ValueError("Exactly one of filename and data_label must be"
                             " None.")

        if filename is not None:
            if filename in self.get_files():
                return True
            return False

        if data_label is not None:
            try:
                self.get_filename(data_label, params)
                return True
            except FileNotFoundError:
                return False


    # ---------------------------------
    # Switching between files and parameters
    # ---------------------------------
    def get_data_label_params(self, filename):
        """Retrieve a data_label and params from the catalog dict
        from the given filename.
        """
        if not self.has_file(filename=filename):
            raise FileNotFoundError(f"No file {filename} in the catalog.")
        index = self._catalog_dict['files'].index(filename)
        return self._catalog_dict['(data_label, parameter) pairs'][index]

    def get_data_label(self, filename):
        """Retrieve a data_label from the catalog dict
        from the given filename.
        """
        return self.get_data_label_params(filename)[0]

    def get_parameters(self, filename):
        """Retrieve the parameters associated with a file
        from the catalog dict from the given filename.
        """
        return self.get_data_label_params(filename)[1]


    def get_filename(self, data_label, params):
        """Retrieve a filename from the catalog dict
        from the given data_label and params.
        """
        # Verifying that the parameters are valid
        params = self.configure_parameters(params)

        # Checking if the data name is recognized
        warn_behavior = "error"
        if self._verbose < 2:
            warn_behavior = "warn"
        if self._verbose < 1:
            warn_behavior = "ignore"

        check_if_recognized(data_label,
                            self._catalog_dict['recognized names'],
                            "data name",
                            default_action=warn_behavior)

        # Getting info for the given params from the catalog
        yaml_key = dict_to_yaml_key(params)

        return self.filename_from_yaml_key(data_label, yaml_key)


    def get_yaml_key(self, filename):
        """Retrieve the yaml key associated with a given
        filename from the catalog dict.
        """
        if not self.has_file(filename=filename):
            raise FileNotFoundError(f"No file {filename} in the catalog.")

        # Looping through all the dicts in the catalog
        # which are associated with a data_label
        for _, data_label_entries in self._catalog_dict.items():
            if not isinstance(data_label_entries, dict):
                continue
            for yaml_key, entry in data_label_entries.items():
                if entry['filename'] == filename:
                    return yaml_key
        assert False, "Did not find the filename in the catalog, but " \
            "expected to find it: self.has_file(filename) returned True."


    def filename_from_yaml_key(self, data_label, yaml_key):
        """Retrieve a filename associated with the given
        data label and yaml key from the catalog.
        """
        try:
            catalog_entry = self._catalog_dict[data_label].get(yaml_key)
        except KeyError as exc:
            raise FileNotFoundError(f"\n"
                    "Could not find data name {data_label} "
                    f"and yaml_key {yaml_key} in the catalog.")\
                    from exc

        return catalog_entry['filename']


    # ---------------------------------
    # Datanames and parameters
    # ---------------------------------
    def data_labels_and_parameters(self):
        """Retrieve all data names and parameters in the catalog."""
        return self._catalog_dict['(data_label, parameter) pairs']

    def params_to_filename(self, data_label, params):
        """Retrieve a filename from the catalog."""
        try:
            return self.get_filename(data_label, params)
        except FileNotFoundError:
            return None

    def filename_to_params(self, filename):
        """Get the data name and parameters associated with a
        file in the catalog.
        """
        files = self.get_files()
        if filename not in files:
            return None
        labels_params = self.data_labels_and_parameters()
        return labels_params[files.index(filename)]
