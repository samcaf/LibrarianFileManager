import tkinter as tk
import os

from tkinter import ttk

from librarian.gui.librarian_gui import beige, black


class PlotterGUI():
    def __init__(self, root, plot_types,
                 catalogs,figure_catalog,
                 **kwargs):
        self.root = root
        self.root.geometry("750x500")
        title = kwargs.get("title", "LFM Plotter")
        self.root.title(title)
        self.root.configure(bg="grey")

        # Plot types and catalogs
        self.plot_types = plot_types
        self.catalogs = catalogs
        self.catalog_dict = {catalog.name():
                             catalog for catalog in catalogs}
        self.catalog_names = self.catalog_dict.keys()
        self.figure_catalog = figure_catalog

        # GUI plot entry information
        self.plot_entries = []
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

        # Create frame containing plots and metadata
        self.create_plot_frame(main_frame)


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
            fg="white",
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
            bg=beige,
            fg="black",
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
            bg=beige,
            fg=black,
            command=self.add_plot_entry
        )
        add_plot_button.grid(row=1, column=0, sticky="e", padx=20, pady=10)

        plot_label = tk.Label(
            plot_intro,
            text="Plot Type:",
            font=("Helvetica", 16, "bold"),
            fg="light grey"
        )
        plot_label.grid(row=0, column=1, padx=5)

        plot_label = tk.Label(
            plot_intro,
            text="Catalog:",
            font=("Helvetica", 16, "bold"),
            fg="light grey"
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
            fg="white"
        )
        label.grid(row=0, column=0, padx=5)

        button_frame = tk.Frame(plot_frame)
        button_frame.grid(row=1, column=0, sticky=tk.W, padx=20, pady=10)

        remove_plot_button = tk.Button(
            button_frame,
            text="Remove Plot",
            font=("Helvetica", 12),
            bg=beige,
            fg=black,
            command=lambda frame=plot_frame: \
                self.remove_plot_entry(frame)
        )
        remove_plot_button.grid(row=0, column=0,
                                   padx=5)

        # Setting up easy retrieval of metadata
        self.plot_entries.append(plot_frame)
        self.plot_type_by_entry[plot_frame] = plot_type
        self.catalog_by_entry[plot_frame] = catalog_name

        # Parameters
        parameter_group_frame = tk.Frame(plot_frame)
        parameter_group_frame.grid(row=2, column=0,
                                  columnspan=4,
                                  sticky=tk.W,
                                  padx=20, pady=10)

        add_parameter_button = tk.Button(
            button_frame,
            text="Add Plot Parameter",
            font=("Helvetica", 12),
            bg=beige,
            fg=black,
            command=lambda: \
                self.add_plot_parameter(parameter_group_frame)
        )
        add_parameter_button.grid(row=0, column=1, sticky="w",
                                 padx=10, pady=5)

        self.plot_parameters_by_entry[plot_frame] = {}

        # Adding parameters for the plot
        self.fill_parameters(parameter_group_frame,
                             parameters, defaults,
                             catalog=self.catalog_dict[catalog_name],
                             **kwargs)

        return plot_frame, parameter_group_frame


    def fill_parameters(self, parameter_group_frame,
                        parameters, defaults,
                        catalog=None):
        """Fills in parameters and defaults for a plot entry"""
        # If none are given, use the parameters associated with the GUI
        # instance
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

        # Otherwise, if the catalog is also given
        if parameters is not None and catalog is not None:
            # Concatenating the catalog's parameters with the given
            # parameters
            catalog_dict = catalog.as_dict()
            catalog_parameters = catalog_dict["parameter types"].keys()
            parameters = list(set(list(parameters) + list(catalog_parameters)))
            # Updating the catalog's default values with the given
            # default values
            catalog_defaults = catalog_dict["default parameters"]
            if catalog_defaults is None:
                catalog_defaults = {}
            defaults = dict(**catalog_defaults, **defaults)

        # Looping over parameters and adding them to the GUI
        for parameter in sorted(parameters):
            default = defaults.get(parameter, None)
            self.add_plot_parameter(parameter_group_frame,
                                    parameter, default)


    def remove_plot_entry(self, entry_frame):
        self.plot_parameters_by_entry.pop(entry_frame)
        self.plot_entries.remove(entry_frame)
        self.plot_type_by_entry.pop(entry_frame)
        self.catalog_by_entry.pop(entry_frame)
        entry_frame.grid_forget()

    def add_plot_parameter(self, parameter_group_frame,
                           key=None, value=None):
        parameter_frame = tk.Frame(parameter_group_frame)

        parameter_frame.grid(row=len(parameter_group_frame.grid_slaves()) + 2,
                            column=0, columnspan=5,
                            sticky="w", padx=10, pady=5)

        new_row = 0

        if len(parameter_group_frame.grid_slaves()) == 1:
            key_label = tk.Label(
                parameter_frame,
                text="Name:",
                font=("Helvetica", 12),
                fg="white",
            )
            value_label = tk.Label(
                parameter_frame,
                text="Value:",
                font=("Helvetica", 12),
                fg="white",
            )

            key_label.grid(row=0, column=1, sticky="w")
            value_label.grid(row=0, column=2, sticky="w")
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
            bg=beige,
            fg=black,
            command=lambda: \
                self.remove_plot_parameter(parameter_frame)
        )
        remove_parameter_button.grid(row=new_row, column=0,
                                    sticky="w",
                                    padx=10, pady=5)

        self.plot_parameters_by_entry[parameter_group_frame.master][parameter_frame] \
            = (parameter_key_entry, parameter_val_entry)

        return parameter_frame


    def remove_plot_parameter(self, parameter_frame):
        self.plot_parameters_by_entry[parameter_frame.master.master].pop(parameter_frame)
        parameter_frame.destroy()


    def create_plots(self, destroy_root=True):
        """Loops over all plot entries and retrieves the plot_type,
        catalog, and parameters.

        Then, calls the (not implemented) create_plot method
        which will eventually create plots.
        """
        for plot_frame in self.plot_entries:
            # Catalog and plot type
            catalog = self.catalog_dict[self.catalog_by_entry[plot_frame]]
            plot_type = self.plot_type_by_entry[plot_frame]

            # Plot parameters
            parameters = {}
            for parameter_frame in self.plot_parameters_by_entry[plot_frame]:
                key, value = self.plot_parameters_by_entry[plot_frame][parameter_frame]
                parameters[key.get()] = value.get()

            # Making plot
            self.create_plot(plot_type, catalog, parameters)

        # Opening the figure catalog in a file explorer
        os.system("open " + str(self.figure_catalog.dir()))

        # Closing the window once the job is complete
        if destroy_root:
            self.root.destroy()
            raise SystemExit(0)

    def create_plot(self, plot_type, catalog, parameters):
        raise NotImplementedError
