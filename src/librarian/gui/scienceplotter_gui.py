import tkinter as tk
import os

from tkinter import ttk

from librarian.gui.librarian_gui import beige, black
from librarian.gui.plotter_gui import PlotterGUI


class SciencePlotterGUI(PlotterGUI):
    # TODO: Re-write create_plot_frame to allow for the selection of
    # TODO:     multiple catalogs
    # TODO:     (and... maybe change behavior plot type, since all
    # TODO:     plots should be scienceplots of different formats?)

    # DEBUG: I don't think any re-writing needs to be done for
    # DEBUG:     add_plot_entry...
    # DEBUG:     (after debugging, can delete this comment)

    def fill_parameters(self, parameter_group_frame,
                        parameters, defaults,
                        catalog=None,
                        varied_parameter_names=None):
        """Fills in parameters and defaults for a plot entry"""
        # If none are given, use the parameters associated with the GUI
        # instance
        if parameters is None:
            parameters = self.plot_parameters
        if defaults is None:
            defaults = self.plot_parameter_defaults
        if varied_parameter_names is None:
            varied_parameter_names = []

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
            vary = parameter in varied_parameter_names
            self.add_plot_parameter(parameter_group_frame,
                                    key=parameter,
                                    value=default,
                                    vary=vary)

    def add_plot_parameter(self, parameter_group_frame,
                           key=None, value=None, vary=False):
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
            vary_label = tk.Label(
                parameter_frame,
                text="Vary?",
                font=("Helvetica", 12),
                fg="white",
            )

            key_label.grid(row=0, column=1, sticky="w")
            value_label.grid(row=0, column=2, sticky="w")
            vary_label.grid(row=0, column=3, sticky="w")
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

        parameter_vary = tk.BooleanVar()
        parameter_vary_entry = tk.Checkbutton(
            parameter_frame,
            variable=parameter_vary,
            onvalue=1, offvalue=0
        )
        parameter_vary_entry.grid(row=new_row, column=3, sticky="w",
                                   padx=10, pady=5)
        parameter_vary.set(vary)

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
            = (parameter_key_entry, parameter_val_entry, parameter_vary)

        return parameter_frame

    def create_plots(self, destroy_root=False):
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
            varied_parameter_names = []
            for parameter_frame in self.plot_parameters_by_entry[plot_frame]:
                key, value, vary = self.plot_parameters_by_entry[plot_frame][parameter_frame]
                parameters[key.get()] = value.get()
                if vary.get():
                    varied_parameter_names.append(key.get())

            # Making plot
            self.create_plot(plot_type, catalog, parameters,
                             varied_parameter_names)

        # Opening the figure catalog in a file explorer
        os.system("open " + str(self.figure_catalog.dir()))

        # Closing the window once the job is complete
        if destroy_root:
            self.root.destroy()
            raise SystemExit(0)

    def create_plot(self, plot_type, catalog, parameters,
                    varied_parameter_names):
        raise NotImplementedError
