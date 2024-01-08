import tkinter as tk
import os

from tkinter import ttk

from numpy import unique

from librarian.gui.librarian_gui import beige, black

# ========================================================
# TODO: Make it so that the plot frame (with scroll bars)
# TODO:     takes up the horizontal extent of the screen
# ========================================================

_MACOS_COLOR_SCHEME = {'background': "grey",
                       'text': black,
                       'header': 'white',
                       'button': beige}

_UBUNTU_COLOR_SCHEME = {'background': black,
                        'text': black,
                        'header': black,
                        'button': beige}

DEFAULT_COLOR_SCHEME = _UBUNTU_COLOR_SCHEME


class PlotterGUI():
    def __init__(self, root, plot_types,
                 catalogs,figure_catalog,
                 **kwargs):
        # ====================================
        # Main Features
        # ====================================
        # --------------------------------
        # Root Window
        # --------------------------------
        self.root = root
        self.root.geometry(kwargs.get("geometry", "750x500"))

        self._color_scheme = kwargs.get('color_scheme',
                                        DEFAULT_COLOR_SCHEME)

        title = kwargs.get("title", "LFM Plotter")
        self.root.title(title)
        self.root.configure(bg=self._color_scheme['background'])

        # --------------------------------
        # Default information
        # --------------------------------
        # Plot types and catalogs
        self.plot_types = plot_types
        self.catalogs = catalogs
        self.catalog_dict = {catalog.name():
                             catalog for catalog in catalogs}
        self.catalog_names = self.catalog_dict.keys()
        self.figure_catalog = figure_catalog

        # - - - - - - - - - - - - - - - -
        # GUI plot entry information
        # - - - - - - - - - - - - - - - -
        # List of plot entries
        self.plot_entries = []

        # Dicts of the form {plot_entry: info}
        # where info is (plot_type, catalog, and parameters),
        # respectively
        self.plot_type_by_entry = {}
        self.catalog_by_entry = {}
        self.plot_parameters_by_entry = {}

        # Default plot entry information
        self.default_plot_type = kwargs.get("default_plot_type",
                                            "Select Plot Type")
        self.default_catalog = kwargs.get("default_catalog",
                                          "Select Catalog")
        self.plot_parameters = kwargs.get("plot_parameters", None)
        self.plot_parameter_defaults = kwargs.get("plot_parameter_defaults",
                                                  None)

        # ====================================
        # Optional Features
        # ====================================

        # --------------------------------
        # Parameter Groups
        # --------------------------------
        # GUI does not group parameters by default:
        self.group_parameters = False

        # GUI only groups parameters if the user
        # specifies parameters_by_group in kwargs
        parameter_groups = kwargs.get("parameter_groups", None)
        # (format: {group_name: [parameters in group]})

        if parameter_groups is not None:
            self.group_parameters = True
            self.parameter_groups = parameter_groups

            # - - - - - - - - - - - - - - - -
            # Setting groups of parameters
            # - - - - - - - - - - - - - - - -
            # Set of parameter names associated with different groups
            # that will be grouped at the time of GUI creation
            self.parameters_by_group = {
                param_name: group_name
                    for group_name in parameter_groups.keys()
                    for param_name in parameter_groups[group_name]
            }
            # (format: {parameter_name: group_name})

            # - - - - - - - - - - - - - - - -
            # Default visibility of each group
            # - - - - - - - - - - - - - - - -
            # Setup of tk.BooleanVars to keep track of the visibility
            self.group_visibility = {
                group_name: tk.BooleanVar()
                for group_name in self.parameter_groups.keys()
            }
            self.group_visibility[None] = tk.BooleanVar()
            self.group_visibility[None].set(True)

            # Getting user-specified visibility of each group
            visible_groups = \
                    kwargs.get("visible_groups", None)
            # (format: [group_name1, group_name2, ...])
            if visible_groups is None:
                visible_groups = []
            assert set(visible_groups).issubset(
                set(self.parameter_groups.keys())
                ), "The set of visible groups of "\
                f"parameters ({visible_groups=}) "\
                "must be a subset of the set of "\
                "given parameter groups "\
                f"({unique(self.parameter_groups.keys())=})."

            # Setting the visibility by setting the BooleanVars
            for group_name in self.parameter_groups.keys():
                if group_name in visible_groups:
                    self.group_visibility[group_name].set(True)
                else:
                    self.group_visibility[group_name].set(False)

            # Preparing for the creation of the group frames
            self.parameter_group_frames = {
                group_name: []
                for group_name in parameter_groups.keys()
            }



        # ====================================
        # Frame Creation
        # ====================================
        # --------------------------------
        # Main Frame
        # --------------------------------
        # Create a main frame to hold all the widgets
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create header frame
        header_text = kwargs.get('header_text',
                                 "LibrarianFileManager Plotter")
        self.create_header_frame(main_frame, header_text)
        self.create_plot_button(main_frame)

        # --------------------------------
        # Plot Frame
        # --------------------------------
        # Create frame containing plots and metadata
        self.create_plot_frame(main_frame)

        # ====================================
        # Misc.
        # ====================================
        self.open_dir = kwargs.get("open_dir", False)
        self.destroy_root = kwargs.get("destroy_root", True)


    def create_header_frame(self, parent, text):
        self.header_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.header_frame.grid(row=row_number, column=0,
                               sticky="ew",
                               padx=150, pady=10)

        header_label = tk.Label(
            self.header_frame,
            text=text,
            font=("Helvetica", 20, "bold"),
            fg=self._color_scheme['header'],
        )

        header_label.grid(row=0, column=0, padx=0, pady=10)


    def create_plot_button(self, parent):
        self.button_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.button_frame.grid(row=row_number, column=0,
                               sticky="ew",
                               padx=250, pady=10)

        # Create a button to create the plots
        create_button = tk.Button(
            self.button_frame,
            text="Create Plots",
            font=("Helvetica", 20),
            bg=self._color_scheme['button'],
            fg=self._color_scheme['text'],
            command=self.create_plots
        )
        create_button.grid(row=0, column=0,
                           padx=50, pady=10)


    def create_plot_frame(self, parent):
        self.plot_frame = tk.Frame(parent)
        row_number = len(parent.grid_slaves())
        self.plot_frame.grid(row=row_number, column=0,
                                padx=20, pady=20, sticky="nsew")
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.plot_frame.grid_columnconfigure(0, weight=1)

        plot_intro = tk.Frame(self.plot_frame)
        plot_intro.grid(row=0, column=0, sticky="ew",
                           padx=20, pady=10)

        add_plot_button = tk.Button(
            plot_intro,
            text="Add Plot",
            font=("Helvetica", 16),
            bg=self._color_scheme['button'],
            fg=self._color_scheme['text'],
            command=self.add_plot_entry
        )
        add_plot_button.grid(row=1, column=0, sticky="e", padx=20, pady=10)

        plot_label = tk.Label(
            plot_intro,
            text="Plot Type:",
            font=("Helvetica", 16, "bold"),
            fg=self._color_scheme['header']
        )
        plot_label.grid(row=0, column=1, padx=5)

        plot_label = tk.Label(
            plot_intro,
            text="Catalog:",
            font=("Helvetica", 16, "bold"),
            fg=self._color_scheme['header']
        )
        plot_label.grid(row=0, column=2, padx=5)

        # Make dropdown menus for plot type and catalog
        plot_type = tk.StringVar(plot_intro)
        plot_type.set(self.default_plot_type)
        plot_type_dropdown = tk.OptionMenu(
            plot_intro,
            plot_type,
            *self.plot_types,
        )
        plot_type_dropdown.grid(row=1, column=1, padx=5)
        self.plot_type_dropdown = plot_type_dropdown

        catalog = tk.StringVar(plot_intro)
        catalog.set(self.default_catalog)
        catalog_dropdown = tk.OptionMenu(
            plot_intro,
            catalog,
            *self.catalog_names,
        )
        catalog_dropdown.grid(row=1, column=2, padx=5)
        self.catalog_dropdown= catalog_dropdown


        # Create a plot container frame
        self.plot_container = tk.Frame(self.plot_frame)
        self.plot_container.grid(row=1, column=0, sticky="nsew")

        # Create a scrollbar for the plot container
        scrollbar_y = ttk.Scrollbar(self.plot_container)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Create a scrollbar for the plot and plot container
        scrollbar_x = ttk.Scrollbar(self.plot_container, orient="horizontal")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Create a canvas for the plot and plot container
        canvas = tk.Canvas(self.plot_container,
                           yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        canvas.grid(row=0, column=0, sticky="nsew")

        # Configure the scrollbars
        scrollbar_x.configure(command=canvas.xview)
        scrollbar_y.configure(command=canvas.yview)

        # Configure column width to make the container wider
        self.plot_container.grid_columnconfigure(0, minsize=700)

        # Create a frame inside the canvas to hold the plot entries
        self.plot_entries_frame = tk.Frame(canvas)
        self.plot_entries_frame.pack(fill="both", expand=True)

        canvas.create_window((0, 0), window=self.plot_entries_frame, anchor="nw")

        self.plot_entries_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))


    def add_plot_entry(self, parameters=None, defaults=None, **kwargs):
        plot_frame = tk.Frame(self.plot_entries_frame)
        plot_type = self.plot_type_dropdown.cget("text")
        if plot_type == "Select Plot Type":
            return
        catalog_name = self.catalog_dropdown.cget("text")
        if catalog_name == "Select Catalog":
            return

        plot_frame.grid(row=len(self.plot_entries_frame.grid_slaves()),
                        column=0,
                        sticky=tk.W, padx=20, pady=10)

        label_frame = tk.Frame(plot_frame)
        label_frame.grid(row=0, column=0, sticky=tk.W, padx=20, pady=10)

        label = tk.Label(
            label_frame,
            text=plot_type+" plot for the "+catalog_name+" catalog",
            font=("Helvetica", 18),
            fg=self._color_scheme['header']
        )
        label.grid(row=0, column=0, padx=5)

        button_frame = tk.Frame(plot_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)

        remove_plot_button = tk.Button(
            button_frame,
            text="Remove Plot",
            font=("Helvetica", 12),
            bg=self._color_scheme['button'],
            fg=self._color_scheme['text'],
            command=lambda frame=plot_frame: \
                self.remove_plot_entry(frame)
        )
        remove_plot_button.grid(row=0, column=0,
                                   padx=5)

        legend_frame = tk.Frame(plot_frame)
        legend_frame.grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        key_label = tk.Label(
            legend_frame,
            text="                         Parameter Name:",
            font=("Helvetica", 14),
            fg=self._color_scheme['header'],
        )
        value_label = tk.Label(
            legend_frame,
            text="Parameter Value:",
            font=("Helvetica", 14),
            fg=self._color_scheme['header'],
        )

        key_label.grid(row=0, column=0, padx=100, sticky="w")
        value_label.grid(row=0, column=1, padx=10, sticky="w")

        # Setting up easy retrieval of metadata
        self.plot_entries.append(plot_frame)
        self.plot_type_by_entry[plot_frame] = plot_type
        self.catalog_by_entry[plot_frame] = catalog_name

        # Parameters
        plot_subframe = tk.Frame(plot_frame)
        plot_subframe.grid(row=3, column=0,
                           columnspan=4,
                           sticky=tk.W,
                           padx=20, pady=10)

        add_parameter_button = tk.Button(
            button_frame,
            text="Add Plot Parameter",
            font=("Helvetica", 12),
            bg=self._color_scheme['button'],
            fg=self._color_scheme['text'],
            command=lambda: \
                self.add_plot_parameter(plot_subframe)
        )
        add_parameter_button.grid(row=0, column=1, sticky="w",
                                 padx=10, pady=5)

        self.plot_parameters_by_entry[plot_frame] = {}

        # Adding parameters for the plot
        self.fill_plot_subframe(plot_subframe,
                                parameters, defaults,
                                catalog=self.catalog_dict[catalog_name],
                                **kwargs)

        return plot_frame, plot_subframe


    def fill_plot_subframe(self, plot_subframe,
                           parameters, defaults,
                           catalog=None, **kwargs):
        """Fills in parameters and defaults for a plot entry,
        organized by groups
        """
        # ====================================
        # Initializing Parameters
        # ====================================
        # If none are given, use the parameters associated with
        # the GUI instance
        if parameters is None:
            parameters = self.plot_parameters
        if defaults is None:
            defaults = self.plot_parameter_defaults

        # If they are still none, use the catalog's parameters
        if parameters is None:
            if catalog is None:
                raise ValueError("Cannot give no parameters without a catalog")
            catalog_dict = catalog.as_dict()
            parameters = catalog_dict["parameter types"].keys()
            defaults = catalog_dict["default parameters"]
        if defaults is None:
            defaults = {}

        # If the catalog is also given
        if parameters is not None and catalog is not None:
            # Concatenating the catalog's parameters
            # with the given parameters
            catalog_dict = catalog.as_dict()
            catalog_parameters = catalog_dict["parameter types"].keys()
            parameters = list(set(list(parameters) + list(catalog_parameters)))
            # Updating the catalog's default values with the given default values
            catalog_defaults = catalog_dict["default parameters"]
            if catalog_defaults is None:
                catalog_defaults = {}
            catalog_defaults.update(defaults)
            defaults = catalog_defaults.copy()
            del catalog_defaults  # Preventing use of catalog_defaults

        # ====================================
        # Filling Parameters in the GUI w/o Grouping
        # ====================================
        # If grouping is not enabled, fill parameters alphabetically
        if not self.group_parameters:
            self.fill_parameter_group_frame(plot_subframe,
                                           parameters, defaults,
                                           **kwargs)
            return plot_subframe

        # ====================================
        # Filling Parameters in the GUI w/ Grouping
        # ====================================
        # Looping over parameters and adding them to the GUI,
        # organized by groups
        for group, group_parameters in self.parameter_groups.items():
            group_frame = tk.Frame(plot_subframe)
            group_frame.grid(row=len(plot_subframe.grid_slaves()) + 2,
                             column=0, columnspan=5,
                             sticky="w", padx=10, pady=5)

            # Add a label for the group
            group_label = tk.Label(
                group_frame,
                text=group,
                font=("Helvetica", 16, "bold"),
                fg=self._color_scheme['header']
            )
            group_label.grid(row=0, column=0, padx=5)

            # Add a toggle button for group visibility
            toggle_button = tk.Button(
                group_frame,
                text="Collapse" if self.group_visibility[group].get() else "Expand",
                font=("Helvetica", 12),
                bg=self._color_scheme['button'], fg=self._color_scheme['text'],
                command=lambda group_info=(group, group_frame): \
                        self.toggle_group_visibility(*group_info)
            )
            toggle_button.grid(row=0, column=1, padx=5)

            # Add parameters associated with the group
            self.parameter_group_frames[group] = \
                    self.fill_parameter_group_frame(group_frame,
                                                    group_parameters,
                                                    defaults, **kwargs)

            # Toggling group visibility twice, if relevant, to make
            # groups that should not be visible -> invisible
            if not self.group_visibility[group].get():
                for _ in range(2):
                    self.toggle_group_visibility(group, group_frame)


        return plot_subframe


    def fill_parameter_group_frame(self, parameter_group_frame,
                                   parameters, defaults,
                                   **kwargs):
        """Fills in parameters and defaults for a plot entry.
        Must return a list of all frames in the group (for
        consistency with parameter grouping/buttons to toggle
        groups of parameters).
        """
        # Looping over parameters and adding them to the GUI
        all_frames_in_group = [self.add_plot_parameter(
                                parameter_group_frame,
                                key=parameter,
                                value=defaults.get(parameter, None))
                               for parameter in sorted(parameters)]

        return all_frames_in_group


    def toggle_group_visibility(self, group, group_frame):
        """Toggles the visibility of a group of parameters."""
        assert self.group_parameters, "Should not be asked to "\
            "toggle group visibility if group_parameters is False "\
            "(i.e. if user did not specify parameters_by_group "\
            "in kwargs during initialization of PlotterGUI)."

        # Toggle the visibility state
        self.group_visibility[group].set(
            not self.group_visibility[group].get())

        for parameter_frame in self.parameter_group_frames[group]:
            parameter_frame.grid_forget()

        # Check the visibility state and re-grid the parameters accordingly
        if self.group_visibility[group].get():
            for parameter_frame in self.parameter_group_frames[group]:
                parameter_frame.grid(
                    row=len(group_frame.grid_slaves()),
                    column=0, columnspan=5,
                    sticky="w", padx=10, pady=5)

        # Add a toggle button for group visibility
        toggle_button = tk.Button(
            group_frame,
            text="Collapse" if self.group_visibility[group].get() else "Expand",
            font=("Helvetica", 12),
            bg=self._color_scheme['button'], fg=self._color_scheme['text'],
            command=lambda group_info=(group, group_frame): \
                    self.toggle_group_visibility(*group_info)
        )
        toggle_button.grid(row=0, column=1, padx=5)


    def remove_plot_entry(self, entry_frame):
        self.plot_parameters_by_entry.pop(entry_frame)
        self.plot_entries.remove(entry_frame)
        self.plot_type_by_entry.pop(entry_frame)
        self.catalog_by_entry.pop(entry_frame)
        entry_frame.grid_forget()


    def add_plot_parameter(self, parameter_group_frame,
                           key=None, value=None,
                           group=None):
        assert group in self.parameter_groups.keys(), "Group must be one "\
            "of the groups specified in the parameter_groups "\
            "dictionary given to the PlotterGUI constructor."\
            "({group=}, {self.parameter_groups.keys()=})"

        parameter_frame = tk.Frame(parameter_group_frame)

        parameter_frame.grid(row=len(parameter_group_frame.grid_slaves()) + 2,
                             column=0, columnspan=5,
                             sticky="w", padx=10, pady=5)

        new_row = 0

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

        # Defaults
        if key is not None:
            parameter_key_entry.insert(tk.END, key)
        else:
            parameter_key_entry.insert(tk.END, "Parameter Key")

        if value is not None:
            parameter_val_entry.insert(tk.END, value)
        else:
            parameter_val_entry.insert(tk.END, "")

        # Button to remove plot parameter
        remove_parameter_button = tk.Button(
            parameter_frame,
            text="Remove",
            font=("Helvetica", 12),
            bg=self._color_scheme['button'],
            fg=self._color_scheme['text'],
            command=lambda: self.remove_plot_parameter(parameter_frame)
        )
        remove_parameter_button.grid(row=new_row, column=0,
                                      sticky="w",
                                      padx=10, pady=5)

        # Getting the plot entry
        plot_entry = parameter_group_frame.master
        while plot_entry not in self.plot_entries:
            plot_entry = plot_entry.master
        self.plot_parameters_by_entry[plot_entry][parameter_frame] \
            = (parameter_key_entry, parameter_val_entry)

        # Setting up parameter group, if the user wants to group parameters
        if self.group_parameters:
            self.parameter_groups[group].append(parameter_frame)

            # Set the same row for all parameters in the group
            # for parameter_frame_in_group in self.parameter_groups[group]:
            #     parameter_frame_in_group.grid(row=new_row, column=0, columnspan=5,
            #                                    sticky="w", padx=10, pady=5)

        # Returning the frame containing the parameter/information
        return parameter_frame


    def remove_plot_parameter(self, parameter_frame):
        # Getting plot entry
        plot_entry = parameter_frame.master.master
        while plot_entry not in self.plot_entries:
            plot_entry = plot_entry.master

        self.plot_parameters_by_entry[plot_entry].pop(parameter_frame)
        parameter_frame.destroy()


    def create_plots(self, open_dir=None, destroy_root=None):
        """Loops over all plot entries and retrieves the plot_type,
        catalog, and parameters.

        Then, calls the (not implemented) create_plot method
        which will eventually create plots.
        """
        if open_dir is None:
            open_dir = self.open_dir
        if destroy_root is None:
            destroy_root = self.destroy_root

        for plot_frame in self.plot_entries:
            # Catalog and plot type
            catalog = self.catalog_dict[self.catalog_by_entry[plot_frame]]
            plot_type = self.plot_type_by_entry[plot_frame]

            # Plot parameters
            parameters = {}
            all_plot_params = \
                    self.plot_parameters_by_entry[plot_frame].values()
            for parameter_info in all_plot_params:
                key, value = parameter_info
                parameters[key.get()] = value.get()

            # Making plot
            self.create_plot(plot_type, catalog, parameters)

        # Opening the figure catalog in a file explorer
        if open_dir:
            os.system("open " +
                      str(self.figure_catalog.dir()).replace(" ", r"\ ").\
                            replace("(", r"\(").replace(")", r"\)")
                     )

        # Closing the window once the job is complete
        if destroy_root:
            self.root.destroy()
            raise SystemExit(0)

    def create_plot(self, plot_type, catalog, parameters):
        raise NotImplementedError
