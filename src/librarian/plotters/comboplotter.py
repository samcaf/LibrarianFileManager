"""This module contains the ComboPlotter class,
which is a subclass of the Plotter class designed
to produce plots which take in a set of parameters
describing cataloged data and output plots which
show certain parameters varied in each plot and
certain parameters held fixed.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rc

import itertools

from librarian.actors.plotter import Plotter
from librarian.catalog import dictdiff


# =====================================
# Additional Analysis Utilities
# =====================================
def is_dict_like(arg):
    """Returns true if the argument is dict-like"""
    return hasattr(arg, 'keys') and \
           hasattr(arg, 'values') and \
           hasattr(arg, 'items')


def is_list_like(arg):
    """Returns true if the argument is list-like"""
    return not hasattr(arg, 'strip') and (\
           hasattr(arg, '__iter__') or \
           hasattr(arg, '__getitem__'))


def reusable_iterable(val, convert_string=True):
    """Makes the input into an iterable even if it is
    not a list, tuple, or other iterable (excluding strings)."""
    if hasattr(val, '__iter__') and not isinstance(val, str):
        return [v for v in val]

    if convert_string and isinstance(val, str):
        if val[0] == '[' and val[-1] == ']':
            # If it is a string that looks like a list
            val = val[1:-1].replace('\'', '').\
                replace('\"', '').\
                replace(' ', '').split(',')
            return val
        elif ' ' in val:
            val = val.split(' ')
            return val
        elif ', ' in val:
            val = val.split(', ')
            return val
        elif ',' in val:
            val = val.split(',')
            return val

    return [val]


def distinct_parameters(parameters):
    """Returns an iterable of all of the ``distinct'' parameters
    within parameters, where distinct means that any list-valued
    value in the original list is turned into a list of dicts,
    (i.e. the list is unpacked ``functorially'' into the dicts).
    """
    # Getting the values of the parameters
    values = map(reusable_iterable, parameters.values())

    # so that we can use itertools.product:
    distinct_values = itertools.product(*values)

    # Now we can return a list of dicts:
    return [dict(zip(parameters.keys(), vals))
            for vals in distinct_values]


def distinct_parameter_values(parameters):
    """Creates an iterable of only the values of the parameters
    in the given parameter dict, so that we can iterate over
    distinct values of the parameters.

    The list analog to the dictionary-valued function
    ``distinct_parameters'' above.
    """
    # Getting the values of the parameters
    values = map(reusable_iterable, parameters.values())
    # Returning a list so we have a re-usable iterable
    return reusable_iterable(itertools.product(*values))


# =====================================
# Additional Plotting Utilities
# =====================================

def stamp(left_x, top_y, axes,
          delta_y=0.075,
          textops_update=None,
          **kwargs):
    """Adds a stamp to figures"""
    # Text options
    textops = {'horizontalalignment': 'left',
               'verticalalignment': 'center',
               'fontsize': 8.5,
               'transform': axes.transAxes}
    if isinstance(textops_update, dict):
        textops.update(textops_update)

    # Add text line by line
    for i in range(len(kwargs)):
        y_val = top_y - i*delta_y
        text = kwargs.get('line_' + str(i))
        if text is not None:
            axes.text(left_x, y_val, text,
                    **textops)

def valid_stamp_loc(stamp_loc):
    """Ensures that the stamp_loc given to stamp is valid,
    and raises errors otherwise"""
    if isinstance(stamp_loc, tuple):
        if len(stamp_loc) != 2:
            raise ValueError("If stamp_loc is given as a tuple, it "
                             "must have length 2 (x, y), but "
                             f"stamp_loc = {stamp_loc}")
        return True
    elif stamp_loc is None:
        return True
    return False


# =====================================
# ###########################################
# Main Functionality: ComboPlotter Class
# ###########################################
# =====================================

# TODO: Right now, act_on_catalogs accepts a single dict, whose values
# TODO:     may be lists, as the set of parameters to plot.
# TODO: I would also like to be able to give a list of dicts, each of
# TODO:     which has a single key-value pair, as the set of parameters
# TODO:     (even better would be that each dict in the list could have
# TODO:      lists as values themselves...)


class ComboPlotter(Plotter):
    """Plotter class for plotting sets of data across multiple plots,
    with certain parameters held fixed within each plot, and certain
    parameters varied.

    This is still an abstract class, and usable subclasses must
    implement the `plot_data` method.
    """
    def __init__(self, metadata_defaults=None,
                 varied_parameters=None,
                 accepted_data_labels=None,
                 require_all_files=True,
                 **kwargs):
        """Initializes the ComboPlotter."""
        kwargs['title'] = kwargs.get('title', 'ComboPlot')

        rc('text', usetex=True)
        if metadata_defaults is None:
            metadata_defaults = {}
        if metadata_defaults.get('showlegend', None) is None:
            metadata_defaults['showlegend'] = False

        # - - - - - - - - - - - - - - - - -
        # Basic setup
        # - - - - - - - - - - - - - - - - -
        self.varied_parameters = varied_parameters
        self.accepted_data_labels = accepted_data_labels
        self.require_all_files = require_all_files

        super().__init__(metadata_defaults, **kwargs)


    # =====================================
    # Conditions for Plotting
    # =====================================
    def check_conditions(self, data_label, params):
        """Check if the file_path meets the conditions to be
        acted upon.

        Could be implemented by subclasses for more stringent plots.
        """
        return True


    def consider_dataset(self, data_label,
                         params_to_match,
                         given_data_parameters):
        """Conditions for a dataset to be considered:
        - It must have an accepted data_label
        - It must have the given parameters as a subset
          of the parameters we want to match
        """
        valid_data_label = self.accepted_data_labels is None \
            or data_label in self.accepted_data_labels

        valid_given_params = \
            set(params_to_match.items()).issubset(
                set(given_data_parameters.items()))

        return valid_data_label and valid_given_params


    def good_dataset(self, data_label,
                     params_to_match,
                     given_data_parameters,
                     extra_conditions=None):
        """Conditions for a dataset to be plotted"""
        valid_dataset = self.consider_dataset(data_label,
                                              params_to_match,
                                              given_data_parameters) \
            and self.check_conditions(data_label,
                                      given_data_parameters)

        if extra_conditions is None:
            return valid_dataset
        return valid_dataset and extra_conditions(data_label,
                                                  params_to_match,
                                                  given_data_parameters)


    # =====================================
    # Setting up for parameter iteration
    # =====================================
    def varied_parameters_iterable(self, parameters):
        """Returns an iterable of the varied parameters."""
        varied_parameters = {param: parameters[param]
                             for param in self.varied_parameters}

        return distinct_parameter_values(varied_parameters)


    def fixed_parameters(self, parameters):
        """Returns a dictionary of the fixed parameters."""
        return {param: parameters[param]
                for param in parameters
                if param not in self.varied_parameters}


    def fixed_parameters_iterable(self, parameters):
        """Returns an iterable of the fixed parameters."""
        fixed_parameters = {param: parameters[param]
                            for param in self.fixed_parameters(parameters)}
        return distinct_parameter_values(fixed_parameters)


    # =====================================
    # Pre-plotting
    # =====================================
    def prepare_figure(self, fig, axes,
                       parameters: dict,
                       varied_parameter_names: list):
        """Prepares axes for plotting.
        Useful e.g. for setting up color cycles.
        """
        pass


    # =====================================
    # Post-processing
    # =====================================
    def stamp_axes(self, stamp_loc: tuple, axes,
                   fixed_param_values: dict):
        """Adds a stamp to the given axes associated
        with the parameters that are fixed for the plot
        on those axes.
        """
        # Location of the stamp
        if stamp_loc is None:
            stamp_loc = (0.5, 0.95)

        # Text for the stamp
        stamp_text = {
            f'line_{iparam}': f"{param} = {val}"
                for iparam, (param, val)
                in enumerate(fixed_param_values.items())
            }
        stamp_text.update({'textops_update':
                          {'fontsize': 11,
                           'horizontalalignment': 'center'}
                           })
        if isinstance(axes, list):
            stamp(*stamp_loc, axes[0], **stamp_text)
        else:
            stamp(*stamp_loc, axes, **stamp_text)


    def process_figure(self, fig, axes,
                       fixed_param_values,
                       **kwargs) -> bool:
        """Processes the figure after plotting
        all relevant data.

        Should return True if the figure was valid and/or
        successfully formatted, False if the figure
        was invalid and should not be plotted,
        and should raise an Error if necessary,
        as determined by the user.

        Default code below should always return True
        unless an error is raised by one of the
        used sub-routines.
        """
        stamp_loc = kwargs.get('stamp_loc', None)
        legend_loc = kwargs.get('legend_loc', 'best')

        if not valid_stamp_loc(stamp_loc):
            try:
                stamp_loc = stamp_loc(fixed_param_values)
                assert valid_stamp_loc(stamp_loc)
            except TypeError as err:
                raise TypeError("stamp_loc must be None, "
                                "a tuple, or a function") from err

        self.stamp_axes(stamp_loc, axes, fixed_param_values)

        if kwargs.get('showlegend', self.metadata['showlegend']):
            axes[0].legend(loc=legend_loc)

        # Setting up xlim and ylim if necessary
        if self.metadata.get('xlim', (None, None)) == (None, None)\
                 and\
                 self.metadata.get('ylim', (None, None)) == (None, None):
            # recompute the ax.dataLim
            [ax.relim() for ax in axes]
            # update ax.viewLim using the new dataLim
            [ax.autoscale_view() for ax in axes]

        # Tight layout
        [ax.tight_layout for ax in axes]
        return True

    # =====================================
    # Main Functionality: Plotting
    # =====================================
    def act_on_catalogs(self, catalogs,
                        parameters,
                        local_rc=True,
                        conditions=None,
                        fig_kwargs=None,
                        close_figure=True,
                        **kwargs):
        """Plots datasets from the given catalogs across
        several figures, holding certain parameters fixed
        within each plot and varied others.
        """
        # ---------------------------------
        # Plot options
        # ---------------------------------
        if fig_kwargs is None:
            def fig_kwargs(data_label, params):
                return {}

        stamp_loc = kwargs.pop('stamp_loc', None)
        if stamp_loc is None:
            def stamp_loc(fixed_param_values):
                return None

        fig_catalog = kwargs.pop('fig_catalog', None)
        figure_label = kwargs.pop('figure_label', None)
        if fig_catalog is None:
            assert figure_label is not None, \
                "Must provide figure_label to save to figure catalog."

        reporter = kwargs.pop('reporter', None)
        if reporter is not None:
            assert fig_catalog is not None, \
                "Must provide fig_catalog in order to make reports."

        # ---------------------------------
        # Preparation for parameter checking
        # ---------------------------------
        # Preparing to check for files which are in
        # the given parameters but not in one of the
        # given catalogs
        missing_file = False

        # Also, we will continue searching for files with the
        # given parameters even if we find one missing file, to
        # provide information about all missing files to the user.
        # However, we may not continue plotting the associated datasets,
        # to save time
        continue_plotting = True

        # - - - - - - - - - - - - - - - - -
        # Separating parameters
        # - - - - - - - - - - - - - - - - -
        self.logger.info("\n# =======================================")
        self.logger.info("# Creating plots:")
        self.logger.info("# =======================================")

        # Single set of parameters, with possible lists of values
        if is_dict_like(parameters):
            fixed_param_names = self.fixed_parameters(parameters).keys()
            fixed_param_iter = self.fixed_parameters_iterable(parameters)

            varied_param_names = self.varied_parameters
            varied_param_iter = self.varied_parameters_iterable(parameters)

            # The set of FIXED PARAMETERS for each figure
            fixed_params_dicts = [dict(zip(fixed_param_names,
                                              fixed_param_set))
                                 for fixed_param_set in fixed_param_iter]

            # The set of VARIED PARAMETERS for each figure
            varied_params_dicts = [dict(zip(varied_param_names,
                                                   varied_param_set))
                                  for varied_param_set in varied_param_iter]

            delim_a = "# ---------------------------------------"
            self.logger.info("# Parameters: (some fixed w/in plots, some varied)")
            self.logger.info(delim_a)
            for key, val in parameters.items():
                self.logger.info(f"#\t- {key}: {val} "
                    +("(varied)" if key in varied_param_names
                      else "(fixed)"))
            self.logger.info(delim_a)
            self.logger.info("# =======================================\n")
        # Lists of parameters
        elif is_list_like(parameters):
            fixed_params_dicts = []
            varied_params_dicts = []
            for param_dict in parameters:
                assert is_dict_like(param_dict), \
                    "Each element of parameters must be a dict, "\
                    "but one of the elements is not."\
                    f"\n\n{parameters=}\nhas element\n{param_dict}"
                fixed_params_dicts.append(
                    {key: val for key, val in param_dict.items()
                     if key not in self.varied_parameters}
                )
                varied_params_dicts.append(
                    {key: val for key, val in param_dict.items()
                     if key in self.varied_parameters(param_dict)}
                )
        else:
            raise TypeError("parameters must be a dict (or dict-like) "
                            "or a list of dicts, but "
                            f"{parameters=}")


        # ---------------------------------
        # Loop over individual figures (fixed params sets)
        # ---------------------------------
        self.logger.debug("Looping over figures:")
        for fixed_fig_params in fixed_params_dicts:
            # Setting up for each individual plot,
            fig, axes = self.subplots()
            num_fig_dsets = 0

            # Logging parameters for the figure,
            # and preparing the figure
            self.logger.debug(delim_a)
            self.logger.debug(f"\t* New figure with\n\t{fixed_fig_params = }")

            self.prepare_figure(fig, axes,
                                parameters,
                                varied_param_names)

            self.logger.debug("\tLooping over datasets for the figure:")
            self.logger.debug(f"\t({varied_param_names = })")
            with mpl.rc_context(self.mpl_rc):
                # - - - - - - - - - - - - - - - - -
                # Looping over parameters for each dataset
                # - - - - - - - - - - - - - - - - -
                for varied_params_to_check in varied_params_dicts:
                    # Init _all_ parameters associated with this dataset
                    params_to_check = {**fixed_fig_params,
                                       **varied_params_to_check}
                    self.logger.debug("\t\t* Finding dataset with\n"
                                 f"\t\t{params_to_check = }")

                    # - - - - - - - - - - - - - - - - -
                    # Adding datasets from each catalog
                    # - - - - - - - - - - - - - - - - -
                    for catalog in catalogs:
                        file_paths = catalog.get_files()
                        labels_params = catalog.data_labels_and_parameters()

                        # Configuring parameters for fair comparison
                        params_to_check = catalog.configure_parameters(
                                                        params_to_check)

                        # Finding if the desired dataset exists in
                        # the catalog
                        found_dataset = False
                        for file_path, (data_label, given_params) in \
                                zip(file_paths, labels_params):
                            # Configuring parameters for fair comparison
                            given_params = catalog.configure_parameters(given_params)

                            # Checking if the file has the desired parameters
                            consider_dataset = self.consider_dataset(
                                                    data_label,
                                                    params_to_check,
                                                    given_params)
                            if consider_dataset:
                                # If the desired dataset exists,
                                found_dataset = True
                                good_dataset = self.good_dataset(
                                                    data_label,
                                                    params_to_check,
                                                    given_params,
                                                    extra_conditions=conditions)
                                if good_dataset and continue_plotting:
                                    # and also satisfies given conditions,
                                    # set up kwargs for the plot,
                                    tmp_kwargs = kwargs.copy()
                                    tmp_kwargs.update(
                                        fig_kwargs(data_label, given_params)
                                    )
                                    # and then plot it!

                                    self.file_action(file_path,
                                                     local_rc=False,
                                                     fig=fig, axes=axes,
                                                     parameters=params_to_check,
                                                     **tmp_kwargs)
                                    num_fig_dsets += 1

                        if not found_dataset:
                            # If the desired dataset does not exist in
                            # the catalog, warn the user
                            missing_file = True
                            self.logger.warn('No file with parameters\n\t'
                                  f'{params_to_check}\n'
                                  'and data_label in\n\t'
                                  f'{self.accepted_data_labels}\n'
                                  'found in catalog '
                                  f'{catalog.name()}.\n')
                            # and use debug to print the nearest parameters
                            file_filter = {'data_label': self.accepted_data_labels}
                            closest_param_info = catalog.closest_params(
                                                        params_to_check,
                                                        file_filter)
                            max_agreement, close_labels, close_params = \
                                    closest_param_info
                            self.logger.debug("The most similar params in "
                                         "the catalog agree with "
                                         f"{max_agreement}/{len(params_to_check)}"
                                         " of the desired parameters.")
                            self.logger.debug(f"(There are {len(close_params)} "
                                         "such sets of parameters)")
                            self.logger.log(5, f"\n\t{close_params = }\n")
                            self.logger.debug("\nThey differ by:")

                            for label, params in zip(close_labels,
                                                     close_params):
                                self.logger.debug(f"\t{params}")
                                diff = dictdiff(params_to_check, params)
                                self.logger.debug(f"\t* {label=}: {diff}")

                            # Continuing to search for other files
                            if self.require_all_files and continue_plotting:
                                continue_plotting = False
                                self.logger.warn('No longer plotting '
                                      '(but still searching to ensure '
                                      'all other files are present).\n')

            # - - - - - - - - - - - - - - - - -
            # Figure post-processing
            # - - - - - - - - - - - - - - - - -
            self.logger.debug("\t# - - - - - - - - - - - - - - - - - ")
            self.logger.debug("\tPlotting for this figure complete")
            if continue_plotting:
                self.logger.debug("\tProcessing figure:")
                self.logger.debug(f"\t{fixed_fig_params = }\n")

                # Processing the figure
                if not self.process_figure(fig, axes,
                                           fixed_fig_params):
                    # If it was found to be invalid,
                    # close and continue to the next fig
                    self.logger.warning("\tWARNING: "
                        "Figure was found to be invalid "
                        "during post-processing.")
                    plt.close()
                    continue


                # Setting up a dictionary of parameters for the
                # figure, which includes both the fixed
                # parameters -- with single values --
                # and the varied parameters -- with lists of values
                fig_params = fixed_fig_params.copy()
                fig_params.update(
                    ( (key, parameters[key])
                       for key in varied_param_names
                     )
                )

                fig_params.update(self.metadata)


                # Figure info
                delim_b = "\t# - - - - - - - - - -\n"
                self.logger.debug("\n" + delim_b
                          +"\n\tFigure complete!\n"
                          +delim_b)
                self.logger.debug(f"\t\t- {fig_params = }")
                self.logger.debug("\t\t- number of "
                          "datasets in figure: "
                          f"{num_fig_dsets}")

                # Saving figure
                if fig_catalog is not None:
                    self.logger.debug("\n\t\tSaving figure"
                          f" to {fig_catalog.name()}")
                    # Saving figure
                    fig_catalog.savefig(fig,
                                figure_label,
                                fig_params,
                                nested_folder=figure_label)

                # Reporting on figure
                if reporter is not None:
                    self.logger.debug("\n\t\t- Reporting figure to "
                                 f"{reporter}")
                    reporter.report_data_from_catalog(fig_catalog,
                                                      figure_label,
                                                      fig_params)
            self.logger.debug(delim_a + "\n")

        # ---------------------------------
        # Finalizing
        # ---------------------------------
        if missing_file and self.require_all_files:
            raise FileNotFoundError('Not all files found in catalog '
                                    ' (you should see some warnings '
                                    'above). Stopping...\n'
                                    '(if you would like to continue '
                                    'plotting anyway, please set '
                                    'require_all_files=False)')
        if close_figure:
            # Closing figure for memory
            plt.close(fig)
        else:
            return fig, axes



    def act_on_catalog(self, catalog,
                        parameters,
                        local_rc=True,
                        conditions=None,
                        fig_kwargs=None,
                        **kwargs):
        """Plots from only a single catalog."""
        self.act_on_catalogs([catalog], parameters, local_rc,
                             conditions, fig_kwargs,
                             **kwargs)


    def legend_prescription(self, params):
        """Generates a legend entry for the dataset
        corresponding to the given parameters.
        """
        params = {key: val for key, val in params.items()
                  if key in self.varied_parameters}

        # By default, legend entry prints any varied parameters
        if len(params) == 0:
            return None

        self.metadata['showlegend'] = True
        legend_entry = ', '.join([f'{key}={val}'
                                  for key, val in params.items()])
        return legend_entry


    def plot_data(self, data, **kwargs):
        """Plots data in a specified way.
        Example beginning of an implementation below.
        """
        # Plot Setup
        fig, axes = kwargs.get('fig', None), kwargs.get('axes', None)
        assert fig is not None, "Must provide a figure to plot on."
        assert axes is not None, "Must provide a set of axes to plot on."

        # Getting parameters from kwargs
        # (useful if plot style should be parameter-dependent)
        try:
            parameters = kwargs.pop('parameters')
        except KeyError as err:
            raise KeyError("Must provide parameters to plot.") from err

        # Setting up for legend
        legend_prescription = kwargs.pop('legend_prescription',
                                         self.legend_prescription)
        legend_entry = legend_prescription(parameters)

        raise NotImplementedError("Plotter.plot_data() not implemented.")
