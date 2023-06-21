import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

from librarian.librarian import Librarian

black = "#000000"
beige = "#d3d3d3"

class LibrarianGUI:
    def __init__(self, root,
                 loadout_dict=None):
        self.root = root
        self.root.geometry("750x850")
        self.root.title("LibrarianFileManager")
        self.root.configure(bg="grey")

        self.metadata_entries = {}
        self.catalog_entries = {}
        self.catalog_metadata = {}
        self.catalog_parameters = {}
        self.catalog_default_parameters = {}

        # Default to current working directory
        self.project_directory = os.getcwd()

        # Create a main frame to hold all the widgets
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create header frame
        self.create_header_frame(main_frame)
        self.create_librarian_button(main_frame)

        # Create metadata frame
        self.create_metadata_frame(main_frame)

        # Create catalog frame
        self.create_catalog_frame(main_frame)

        # Preparing a particular loadout if one was given
        if loadout_dict is None:
            # Add a metadata entry for the project name
            self.add_project_metadata_entry("Project Name",
                                            "My Project")
        else:
            # Preparing loadout
            project_dir = loadout_dict.get("project directory")
            project_metadata = loadout_dict.get("project metadata")
            catalog_names = loadout_dict.get("catalog names")
            catalog_metadata = loadout_dict.get("catalog metadata")
            catalog_parameters = loadout_dict.get("catalog parameters")
            catalog_defaults = loadout_dict.get("catalog default "
                                                "parameters")

            self.load_presets(project_dir, project_metadata,
                              catalog_names, catalog_metadata,
                              catalog_parameters, catalog_defaults)

    def create_header_frame(self, parent):
        self.header_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.header_frame.grid(row=row_number, column=0,
                               sticky="ew",
                               padx=150, pady=10)

        header_label = tk.Label(
            self.header_frame,
            text="Welcome to Librarian File Manager (LFM)",
            font=("Helvetica", 16, "bold"),
            fg="white",
        )

        intro_label = tk.Label(
            self.header_frame,
            text="Let's create your project!",
            font=("Helvetica", 14),
            fg="white"
        )

        header_label.grid(row=0, column=0, padx=50, pady=10)
        intro_label.grid(row=1, column=0, pady=10)

    def create_librarian_button(self, parent):
        self.button_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.button_frame.grid(row=row_number, column=0,
                               sticky="ew",
                               padx=250, pady=10)

        # Create a button to create the project
        # with a Librarian
        create_button = tk.Button(
            self.button_frame,
            text="Create Project",
            font=("Helvetica", 16),
            bg=beige,
            fg="black",
            command=self.create_project
        )
        create_button.grid(row=0, column=0,
                           padx=50, pady=10)

    def create_metadata_frame(self, parent):
        self.metadata_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.metadata_frame.grid(row=row_number, column=0,
                            padx=20, pady=20,
                            sticky="nsew")
        self.metadata_frame.grid_rowconfigure(0, weight=1)
        self.metadata_frame.grid_columnconfigure(0, weight=1)

        metadata_intro = tk.Frame(self.metadata_frame)
        metadata_intro.grid(row=0, column=0, sticky="ew",
                            padx=20, pady=10)

        metadata_label = tk.Label(
            metadata_intro,
            text="Project Metadata:",
            font=("Helvetica", 20, "bold"),
            fg="white",
        )
        metadata_label.grid(row=0, column=0, sticky="w",
                            padx=20, pady=10)

        add_metadata_button = tk.Button(
            metadata_intro,
            text="Add Project Metadata",
            font=("Helvetica", 10),
            bg=beige,
            fg=black,
            command=self.add_project_metadata_entry
        )
        add_metadata_button.grid(row=0, column=1,
                                 sticky="e",
                                 padx=20, pady=10)

        # Create a button to select the project directory
        select_directory_button = tk.Button(
            metadata_intro,
            text="Select Project Directory",
            font=("Helvetica", 12),
            bg=beige,
            fg="black",
            command=self.select_project_directory
        )
        select_directory_button.grid(row=3, column=0,
                                     columnspan=3, pady=5)

        # Create a metadata container frame
        self.metadata_container = tk.Frame(self.metadata_frame)
        self.metadata_container.grid(row=1, column=0, sticky="nsew")

        # Create a scrollbar for the metadata container
        scrollbar_y = ttk.Scrollbar(self.metadata_container)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Create a scrollbar for the metadata and catalog container
        scrollbar_x = ttk.Scrollbar(self.metadata_container, orient="horizontal")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Create a canvas for the metadata and catalog container
        canvas = tk.Canvas(self.metadata_container,
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Configure the scrollbars
        scrollbar_x.configure(command=canvas.xview)
        scrollbar_y.configure(command=canvas.yview)

        # Configure grid weights to allow expansion
        self.metadata_container.grid_rowconfigure(0, weight=1)
        self.metadata_container.grid_columnconfigure(0, weight=1)

        # Create a canvas for the metadata container
        canvas = tk.Canvas(self.metadata_container,
                           yscrollcommand=scrollbar_y.set)
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar_y.configure(command=canvas.yview)
        scrollbar_x.configure(command=canvas.xview)

        # Configure column width to make the container wider
        self.metadata_container.grid_columnconfigure(0, minsize=700)

        # Create a frame inside the canvas to hold the metadata entries
        self.metadata_entries_frame = tk.Frame(canvas)
        self.metadata_entries_frame.pack(fill="both", expand=True)

        canvas.create_window((0, 0), window=self.metadata_entries_frame, anchor="nw")

        self.metadata_entries_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    def create_catalog_frame(self, parent):
        self.catalog_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.catalog_frame.grid(row=row_number, column=0,
                                padx=20, pady=20, sticky="nsew")
        self.catalog_frame.grid_rowconfigure(0, weight=1)
        self.catalog_frame.grid_columnconfigure(0, weight=1)

        catalog_intro = tk.Frame(self.catalog_frame)
        catalog_intro.grid(row=0, column=0, sticky="ew",
                           padx=20, pady=10)

        catalog_label = tk.Label(
            catalog_intro,
            text="Catalog:",
            font=("Helvetica", 20, "bold"),
            fg="white",
        )
        catalog_label.grid(row=0, column=0, sticky="w",
                           padx=20, pady=10)

        add_catalog_button = tk.Button(
            catalog_intro,
            text="Add Catalog Entry",
            font=("Helvetica", 10),
            bg=beige,
            fg=black,
            command=self.add_catalog_entry
        )
        add_catalog_button.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        # Create a catalog container frame
        self.catalog_container = tk.Frame(self.catalog_frame)
        self.catalog_container.grid(row=1, column=0, sticky="nsew")

        # Create a scrollbar for the catalog container
        scrollbar_y = ttk.Scrollbar(self.catalog_container)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Create a scrollbar for the catalog and catalog container
        scrollbar_x = ttk.Scrollbar(self.catalog_container, orient="horizontal")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Create a canvas for the catalog and catalog container
        canvas = tk.Canvas(self.catalog_container,
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Configure the scrollbars
        scrollbar_x.configure(command=canvas.xview)
        scrollbar_y.configure(command=canvas.yview)

        # Configure column width to make the container wider
        self.catalog_container.grid_columnconfigure(0, minsize=700)

        # Create a frame inside the canvas to hold the catalog entries
        self.catalog_entries_frame = tk.Frame(canvas)
        self.catalog_entries_frame.pack(fill="both", expand=True)

        canvas.create_window((0, 0), window=self.catalog_entries_frame, anchor="nw")

        self.catalog_entries_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

    def select_project_directory(self):
        directory = filedialog.askdirectory(initialdir=self.project_directory)
        self.project_directory = directory

    def add_project_metadata_entry(self, key=None, value=None):
        metadata_entry_frame = tk.Frame(self.metadata_entries_frame)

        metadata_entry_frame.grid(sticky=tk.W, padx=20, pady=20)

        new_row = 0

        if len(self.metadata_entries_frame.grid_slaves()) == 1:
            key_label = tk.Label(
                metadata_entry_frame,
                text="Key:",
                font=("Helvetica", 12),
                fg="white",
            )
            value_label = tk.Label(
                metadata_entry_frame,
                text="Value:",
                font=("Helvetica", 12),
                fg="white",
            )
            key_label.grid(row=0, column=1, sticky="w")
            value_label.grid(row=0, column=2, sticky="w")
            new_row = 1

        metadata_key_entry = tk.Entry(metadata_entry_frame, font=("Helvetica", 10), width=20)
        metadata_key_entry.grid(row=new_row, column=1, padx=5)

        metadata_value_entry = tk.Entry(metadata_entry_frame,
                                        font=("Helvetica", 10), width=30)
        metadata_value_entry.grid(row=new_row, column=2, padx=5)

        if key is not None:
            metadata_key_entry.insert(tk.END, key)
        if value is not None:
            metadata_value_entry.insert(tk.END, value)

        remove_metadata_button = tk.Button(
            metadata_entry_frame,
            text="Remove",
            font=("Helvetica", 10),
            fg=black,
            command=lambda frame=metadata_entry_frame: \
                self.remove_metadata_entry(frame)
        )
        remove_metadata_button.grid(row=new_row, column=0, padx=5)

        self.metadata_entries[metadata_entry_frame] = \
            (metadata_key_entry, metadata_value_entry)

    def remove_metadata_entry(self, entry_frame):
        self.metadata_entries.pop(entry_frame)
        entry_frame.grid_forget()

    def add_catalog_entry(self, catalog_name=None):
        catalog_frame = tk.Frame(self.catalog_entries_frame)

        catalog_frame.grid(sticky=tk.W, padx=20, pady=10)

        catalog_label = tk.Label(
            catalog_frame,
            text="Catalog Name:",
            font=("Helvetica", 18, "bold"),
            fg="light grey"
        )
        catalog_label.grid(row=0, column=1, padx=5)

        catalog_entry = tk.Entry(catalog_frame,
                                 font=("Helvetica", 10),
                                 width=20)
        catalog_entry.grid(row=0, column=2, padx=5)

        if catalog_name is not None:
            catalog_entry.insert(tk.END, catalog_name)

        remove_catalog_button = tk.Button(
            catalog_frame,
            text="Remove",
            font=("Helvetica", 10),
            bg=beige,
            fg=black,
            command=lambda frame=catalog_frame: \
                self.remove_catalog_entry(frame)
        )
        remove_catalog_button.grid(row=0, column=3,
                                   padx=5)

        # Detailed Metadata
        metadata_group_frame = tk.Frame(catalog_frame)
        metadata_group_frame.grid(row=2, column=1,
                                  columnspan=4,
                                  sticky=tk.W,
                                  padx=20, pady=10)
        add_metadata_button = tk.Button(
            catalog_frame,
            text="Add Catalog Metadata",
            font=("Helvetica", 10),
            bg=beige,
            fg=black,
            command=lambda: \
                self.add_catalog_metadata(metadata_group_frame)
        )
        add_metadata_button.grid(row=1, column=1, sticky="w",
                                 padx=10, pady=5)
        self.catalog_metadata[catalog_frame] = {}

        # Parameters
        parameter_group_frame = tk.Frame(catalog_frame)

        parameter_group_frame.grid(row=3, column=1,
                                  columnspan=4,
                                  sticky=tk.W,
                                  padx=20, pady=10)
        add_parameter_button = tk.Button(
            catalog_frame,
            text="Add Catalog Parameter",
            font=("Helvetica", 10),
            bg=beige,
            fg=black,
            command=lambda: \
                self.add_catalog_parameter(parameter_group_frame)
        )
        add_parameter_button.grid(row=1, column=2, sticky="w",
                                 padx=10, pady=5)
        self.catalog_parameters[catalog_frame] = {}
        self.catalog_default_parameters[catalog_frame] = {}

        # Store the catalog frame and append to the list
        catalog_frame.grid(row=len(self.catalog_entries) + 4,
                           column=0, columnspan=5,
                           sticky="w", padx=10, pady=5)

        self.catalog_entries[catalog_frame] = catalog_entry

        return catalog_frame, metadata_group_frame, parameter_group_frame

    def remove_catalog_entry(self, entry_frame):
        self.catalog_metadata.pop(entry_frame)
        self.catalog_parameters.pop(entry_frame)
        self.catalog_default_parameters.pop(entry_frame)
        self.catalog_entries.pop(entry_frame)
        entry_frame.grid_forget()

    def add_catalog_metadata(self, metadata_group_frame,
                             key=None, value=None):
        metadata_frame = tk.Frame(metadata_group_frame)

        metadata_frame.grid(row=len(metadata_group_frame.grid_slaves()) + 2,
                            column=0, columnspan=5,
                            sticky="w", padx=10, pady=5)

        new_row = 0

        if len(metadata_group_frame.grid_slaves()) == 1:
            key_label = tk.Label(
                metadata_frame,
                text="Key:",
                font=("Helvetica", 12),
                fg="white",
            )
            value_label = tk.Label(
                metadata_frame,
                text="Value:",
                font=("Helvetica", 12),
                fg="white",
            )
            key_label.grid(row=0, column=1, sticky="w")
            value_label.grid(row=0, column=2, sticky="w")

            new_row = 1

        metadata_key_entry = tk.Entry(
            metadata_frame,
            font=("Helvetica", 12),
        )
        metadata_key_entry.grid(row=new_row, column=1, sticky="w",
                                padx=100, pady=5)

        metadata_val_entry = tk.Entry(
            metadata_frame,
            font=("Helvetica", 12),
        )
        metadata_val_entry.grid(row=new_row, column=2, sticky="w",
                                padx=10, pady=5)

        # Defaults
        if key is not None:
            metadata_key_entry.insert(tk.END, key)
        else:
            metadata_key_entry.insert(tk.END, "Metadata Key")

        if value is not None:
            metadata_val_entry.insert(tk.END, value)
        else:
            metadata_val_entry.insert(tk.END, "Metadata Value")

        # Button to remove catalog metadata
        remove_metadata_button = tk.Button(
            metadata_frame,
            text="Remove",
            font=("Helvetica", 12),
            bg=beige,
            fg=black,
            command=lambda: \
                self.remove_catalog_metadata(metadata_frame)
        )
        remove_metadata_button.grid(row=new_row, column=0,
                                    sticky="w",
                                    padx=10, pady=5)

        self.catalog_metadata[metadata_group_frame.master][metadata_frame] \
            = (metadata_key_entry, metadata_val_entry)

        return metadata_frame

    def remove_catalog_metadata(self, metadata_frame):
        self.catalog_metadata[metadata_frame.master.master].pop(metadata_frame)
        metadata_frame.destroy()

    def add_catalog_parameter(self, parameter_group_frame,
                              key=None, value=None, default=None):
        parameter_frame = tk.Frame(parameter_group_frame)

        parameter_frame.grid(row=len(parameter_group_frame.grid_slaves()) + 2,
                            column=0, columnspan=5,
                            sticky="w", padx=10, pady=5)

        new_row = 0

        if len(parameter_group_frame.grid_slaves()) == 1:
            key_label = tk.Label(
                parameter_frame,
                text="Key:",
                font=("Helvetica", 12),
                fg="white",
            )
            value_label = tk.Label(
                parameter_frame,
                text="Value:",
                font=("Helvetica", 12),
                fg="white",
            )
            default_label = tk.Label(
                parameter_frame,
                text="Default:",
                font=("Helvetica", 12),
                fg="white",
            )
            key_label.grid(row=0, column=1, sticky="w")
            value_label.grid(row=0, column=2, sticky="w")
            default_label.grid(row=0, column=3, sticky="w")
            new_row = 1


        parameter_key_entry = tk.Entry(
            parameter_frame,
            font=("Helvetica", 12),
        )
        parameter_key_entry.grid(row=new_row, column=1, sticky="w",
                                padx=100, pady=5)

        parameter_val_entry = tk.Entry(
            parameter_frame,
            font=("Helvetica", 12),
        )
        parameter_val_entry.grid(row=new_row, column=2, sticky="w",
                                padx=10, pady=5)

        default_parameter_entry = tk.Entry(
            parameter_frame,
            font=("Helvetica", 12),
        )
        default_parameter_entry.grid(row=new_row, column=3, sticky="w",
                                padx=10, pady=5)

        # Defaults
        if key is not None:
            parameter_key_entry.insert(tk.END, key)
        else:
            parameter_key_entry.insert(tk.END, "Parameter Key")

        if value is not None:
            parameter_val_entry.insert(tk.END, value)
        else:
            parameter_val_entry.insert(tk.END, "Parameter Value")

        if default is not None:
            default_parameter_entry.insert(tk.END, default)
        else:
            default_parameter_entry.insert(tk.END, "None")

        # Button to remove catalog parameter
        remove_parameter_button = tk.Button(
            parameter_frame,
            text="Remove",
            font=("Helvetica", 12),
            bg=beige,
            fg=black,
            command=lambda: \
                self.remove_catalog_parameter(parameter_frame)
        )
        remove_parameter_button.grid(row=new_row, column=0,
                                    sticky="w",
                                    padx=10, pady=5)

        self.catalog_parameters[parameter_group_frame.master][parameter_frame] \
            = (parameter_key_entry, parameter_val_entry)
        self.catalog_default_parameters[parameter_group_frame.master][parameter_frame] \
            = (parameter_key_entry, default_parameter_entry)

        return parameter_frame

    def remove_catalog_parameter(self, parameter_frame):
        self.catalog_parameters[parameter_frame.master.master].pop(parameter_frame)
        self.catalog_default_parameters[parameter_frame.master.master].pop(parameter_frame)
        parameter_frame.destroy()

    def create_project(self, save=False):
        project_metadata = {}

        project_metadata['Project Location'] = self.project_directory

        for _, metadata_entries in self.metadata_entries.items():
            metadata_key = metadata_entries[0].get()
            metadata_value = metadata_entries[1].get()
            project_metadata[metadata_key] = metadata_value

        catalog_dirs = {}
        for catalog_frame, catalog_entry in self.catalog_entries.items():
            c_name = catalog_entry.get()
            catalog_dirs[c_name] = self.project_directory + "/" + c_name

        catalog_metadata = {}
        for catalog_frame, metadata_entries in self.catalog_metadata.items():
            c_name = self.catalog_entries[catalog_frame].get()
            metadata_dict = {}
            for _, metadata_entries in metadata_entries.items():
                metadata_key = metadata_entries[0].get()
                metadata_value = metadata_entries[1].get()
                metadata_dict[metadata_key] = metadata_value
            catalog_metadata[c_name] = metadata_dict

        catalog_parameters = {}
        # Getting the parameter names (keys) and types (values)
        # for each catalog
        for catalog_frame, parameter_entries in self.catalog_parameters.items():
            c_name = self.catalog_entries[catalog_frame].get()
            parameter_dict = {}
            for _, parameter_entries in parameter_entries.items():
                parameter_key = parameter_entries[0].get()
                parameter_value = parameter_entries[1].get()
                parameter_dict[parameter_key] = parameter_value
            catalog_parameters[c_name] = parameter_dict

        catalog_defaults = {}
        # Getting the parameter default values for each catalog
        for catalog_frame, parameter_entries in self.catalog_default_parameters.items():
            c_name = self.catalog_entries[catalog_frame].get()
            parameter_dict = {}
            for _, parameter_entries in parameter_entries.items():
                parameter_key = parameter_entries[0].get()
                parameter_value = parameter_entries[1].get()
                parameter_dict[parameter_key] = parameter_value
            catalog_defaults[c_name] = parameter_dict

        librarian = Librarian(self.project_directory, project_metadata,
                               catalog_dirs, catalog_metadata,
                               catalog_parameters, catalog_defaults)
        librarian.create_stacks(save)

        # Closing the window once the job is complete
        self.root.destroy()

    def load_project_metadata(self, project_metadata):
        if project_metadata is None:
            return
        for key, value in project_metadata.items():
            self.add_project_metadata_entry(key=key, value=value)
        return

    def load_catalogs(self, catalog_names,
                      catalog_metadata,
                      catalog_parameters,
                      catalog_defaults):
        if catalog_names is None:
            return
        for c_name in catalog_names:
            _, c_meta_frame, c_param_frame =\
                self.add_catalog_entry(c_name)
            if catalog_metadata.get(c_name) is not None:
                for key, value in catalog_metadata[c_name].items():
                    self.add_catalog_metadata(c_meta_frame, key, value)
            if catalog_parameters.get(c_name) is not None:
                for key, value in catalog_parameters[c_name].items():
                    # Getting the default value of the parameter
                    if catalog_defaults is not None:
                        default_value = catalog_defaults.get(c_name)
                    else:
                        default_value = None
                    if default_value is not None:
                        default_value = default_value.get(key)

                    self.add_catalog_parameter(c_param_frame, key, value,
                                               default_value)
        return

    def load_presets(self, project_dir,
                     project_metadata,
                     catalog_names, catalog_metadata,
                     catalog_parameters,
                     catalog_defaults):
        if project_dir is not None:
            self.project_directory = project_dir

        self.load_project_metadata(project_metadata)
        self.load_catalogs(catalog_names, catalog_metadata,
                           catalog_parameters, catalog_defaults)
