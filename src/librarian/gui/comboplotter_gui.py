import tkinter as tk
import os

from tkinter import ttk

from librarian.gui.librarian_gui import beige, black
from librarian.gui.plotter_gui import PlotterGUI


class ComboPlotterGUI(PlotterGUI):
    def fill_parameter_group_frame(self, parameter_group_frame,
                                   parameters, defaults,
                                   varied_parameter_names=None):
        """Fills in parameters and defaults for a plot entry"""
        if varied_parameter_names is None:
            varied_parameter_names = []

        # Looping over parameters and adding them to the GUI
        all_frames_in_group = [self.add_plot_parameter(
                                parameter_group_frame,
                                key=parameter,
                                value=defaults.get(parameter, None),
                                vary=parameter in varied_parameter_names)
                               for parameter in sorted(parameters)]

        return all_frames_in_group


    def add_plot_entry(self, parameters=None, defaults=None, **kwargs):
        plot_frame, plot_subframe = \
            super().add_plot_entry(parameters=parameters,
                                   defaults=defaults,
                                   **kwargs)

        legend_frame = tk.Frame(plot_frame)
        legend_frame.grid(row=2, column=0, sticky=tk.W, padx=20, pady=10)
        key_label = tk.Label(
            legend_frame,
            text="                           "\
                "Parameter Name:",
            font=("Helvetica", 14),
            fg="white",
        )
        value_label = tk.Label(
            legend_frame,
            text="Parameter Value:",
            font=("Helvetica", 14),
            fg="white",
        )
        vary_label = tk.Label(
            legend_frame,
            text="Vary\nParameter?",
            font=("Helvetica", 14),
            fg="white",
        )

        key_label.grid(row=0, column=0, padx=100, sticky="w")
        value_label.grid(row=0, column=1, padx=40, sticky="w")
        vary_label.grid(row=0, column=2, padx=10, sticky="w")

        return plot_frame, plot_subframe


    def add_plot_parameter(self, parameter_group_frame,
                           key=None, value=None, vary=False):
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

        plot_entry = parameter_group_frame.master
        while plot_entry not in self.plot_entries:
            plot_entry = plot_entry.master
        self.plot_parameters_by_entry[plot_entry][parameter_frame] \
            = (parameter_key_entry, parameter_val_entry, parameter_vary)

        return parameter_frame

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
            varied_parameter_names = []
            all_plot_params = \
                    self.plot_parameters_by_entry[plot_frame].values()
            for parameter_info in all_plot_params:
                key, value, vary = parameter_info
                parameters[key.get()] = value.get()
                if vary.get():
                    varied_parameter_names.append(key.get())

            # Making plot
            self.create_plot(plot_type, catalog, parameters,
                             varied_parameter_names)

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

    def create_plot(self, plot_type, catalog, parameters,
                    varied_parameter_names):
        raise NotImplementedError
